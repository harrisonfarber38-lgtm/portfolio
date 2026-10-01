// npm run seed — replaces projects with the content in data.js.
// Contact messages are never touched.
import { pathToFileURL } from "node:url";
import mongoose from "mongoose";
import { connect } from "../db.js";
import Project from "../models/Project.js";
import { projects } from "./data.js";

export async function seed() {
  await Project.deleteMany({});
  await Project.insertMany(projects);
  return { projects: projects.length };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  if (!process.env.MONGODB_URI) {
    console.error("Set MONGODB_URI to seed a real database (the in-memory dev database seeds itself).");
    process.exit(1);
  }
  await connect();
  console.log("seeded", await seed());
  await mongoose.disconnect();
}
