import { cpSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const api = "http://localhost:" + (process.env.API_PORT || 5000);
const repoAssets = fileURLToPath(new URL("../assets", import.meta.url));

// Copy the repo's images, drawing sheets and video into dist/assets so the built site
// works on any static host (Vercel, Netlify, GitHub Pages), not only behind Express.
const copyRepoAssets = () => ({
  name: "copy-repo-assets",
  apply: "build",
  closeBundle() {
    const out = fileURLToPath(new URL("./dist/assets", import.meta.url));
    if (existsSync(repoAssets)) cpSync(repoAssets, out, { recursive: true });
  },
});

export default defineConfig({
  plugins: [react(), copyRepoAssets()],
  // "/assets" is the repo's image folder, so keep the JS/CSS bundle apart
  build: { assetsDir: "static" },
  server: {
    port: 5173,
    proxy: { "/api": api, "/assets": api },
    fs: { allow: [".."] },   // client imports the portfolio data from ../server/src/seed
  },
});
