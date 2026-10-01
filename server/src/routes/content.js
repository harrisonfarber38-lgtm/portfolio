import { Router } from "express";
import { isConnected } from "../db.js";
import Project from "../models/Project.js";
import { education, experience, projects as seedProjects } from "../seed/data.js";

const router = Router();
const hide = "-__v -createdAt -updatedAt";

// Without a database (dev only, see db.js) the same content comes from the seed data.
router.get("/projects", async (req, res) => {
  const type = req.query.type ? String(req.query.type) : null;
  if (!isConnected()) return res.json(seedProjects.filter((p) => !type || p.type === type));
  res.json(await Project.find(type ? { type } : {}, hide).sort("order").lean());
});

router.get("/projects/:slug", async (req, res) => {
  const project = isConnected()
    ? await Project.findOne({ slug: req.params.slug }, hide).lean()
    : seedProjects.find((p) => p.slug === req.params.slug);
  if (!project) return res.status(404).json({ error: "Project not found" });
  res.json(project);
});

// Career history from the resume (static content, versioned with the code).
router.get("/profile", (_req, res) => res.json({ experience, education }));

export default router;
