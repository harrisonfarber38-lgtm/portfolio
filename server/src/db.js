import mongoose from "mongoose";

let memoryServer;

export const isConnected = () => mongoose.connection.readyState === 1;

/**
 * Connects to MONGODB_URI. In development without one, tries an in-memory
 * MongoDB; if that can't start either (it downloads a mongod binary on first
 * use), the API keeps running without a database and serves the seed content.
 * Returns "uri" | "memory" | "none".
 */
export async function connect() {
  const uri = process.env.MONGODB_URI;
  if (uri) {
    await mongoose.connect(uri);
    console.log(`[db] connected to ${mongoose.connection.host}/${mongoose.connection.name}`);
    return "uri";
  }
  if (process.env.NODE_ENV === "production") throw new Error("MONGODB_URI is required in production");
  if (process.env.MEMORY_DB === "0") {
    console.warn("[db] MEMORY_DB=0: running WITHOUT a database (seed content, contact form disabled).");
    return "none";
  }
  try {
    const { MongoMemoryServer } = await import("mongodb-memory-server");
    memoryServer = await MongoMemoryServer.create();
    await mongoose.connect(memoryServer.getUri("bim-portfolio"));
    console.log("[db] MONGODB_URI not set: using an in-memory MongoDB (data resets on restart)");
    return "memory";
  } catch (err) {
    console.warn(`[db] MONGODB_URI not set and in-memory MongoDB unavailable (${err.code || err.message}).`);
    console.warn("[db] Running WITHOUT a database: content is served from seed data, contact form is disabled.");
    console.warn("[db] Set MONGODB_URI in server/.env to enable it.");
    return "none";
  }
}

export async function disconnect() {
  await mongoose.disconnect();
  if (memoryServer) await memoryServer.stop();
}
