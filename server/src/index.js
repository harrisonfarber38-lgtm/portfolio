import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import express from "express";
import helmet from "helmet";
import { connect, disconnect, isConnected } from "./db.js";
import Project from "./models/Project.js";
import content from "./routes/content.js";
import messages from "./routes/messages.js";
import { seed } from "./seed/seed.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(here, "../..");
const CLIENT_DIST = path.join(ROOT, "client", "dist");
const PORT = Number(process.env.PORT) || 5000;

const app = express();
app.set("trust proxy", 1);
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      "img-src": ["'self'", "data:"],
      "style-src": ["'self'", "https://fonts.googleapis.com", "'unsafe-inline'"],
      "font-src": ["'self'", "https://fonts.gstatic.com"],
    },
  },
}));
app.use(express.json({ limit: "20kb" }));

app.get("/api/health", (_req, res) => res.json({ ok: true, database: isConnected() }));
app.use("/api", content);
app.use("/api", messages);
app.use("/api", (_req, res) => res.status(404).json({ error: "Not found" }));

// images and SVG panels shared with the README
app.use("/assets", express.static(path.join(ROOT, "assets"), { maxAge: "7d" }));

// built React app (npm run build) with SPA fallback
if (existsSync(CLIENT_DIST)) {
  app.use(express.static(CLIENT_DIST, { maxAge: "1h", index: false }));
  app.get(/^(?!\/api|\/assets).*/, (_req, res) => res.sendFile(path.join(CLIENT_DIST, "index.html")));
}

app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(500).json({ error: "Something went wrong." });
});

const mode = await connect();
if (mode === "memory" || (mode === "uri" && (await Project.estimatedDocumentCount()) === 0)) {
  console.log("[db] seeded", await seed());
}
const server = app.listen(PORT, () => console.log(`[api] http://localhost:${PORT}`));

for (const sig of ["SIGINT", "SIGTERM"]) {
  process.on(sig, async () => {
    server.close();
    await disconnect();
    process.exit(0);
  });
}
