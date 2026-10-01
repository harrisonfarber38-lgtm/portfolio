import { Router } from "express";
import rateLimit from "express-rate-limit";
import mongoose from "mongoose";
import { isConnected } from "../db.js";
import Message from "../models/Message.js";

const router = Router();

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 5,
  standardHeaders: "draft-8",
  legacyHeaders: false,
  message: { error: "Too many messages. Please try again later." },
});

// Contact form. "website" is a honeypot field: real visitors never see or fill it.
router.post("/messages", limiter, async (req, res) => {
  const { name, email, company, message, website } = req.body ?? {};
  if (website) return res.status(201).json({ ok: true });
  if (!isConnected()) return res.status(503).json({ error: "Messages are unavailable right now. Please reach out on LinkedIn." });
  try {
    await Message.create({ name, email, company, message });
    res.status(201).json({ ok: true });
  } catch (err) {
    if (err instanceof mongoose.Error.ValidationError) {
      const fields = Object.fromEntries(Object.entries(err.errors).map(([k, e]) => [k, fieldError(k, e)]));
      return res.status(400).json({ error: "Please check the highlighted fields.", fields });
    }
    throw err;
  }
});

function fieldError(field, e) {
  if (e.kind === "required") return `${field[0].toUpperCase() + field.slice(1)} is required.`;
  if (field === "email") return "Enter a valid email address.";
  if (e.kind === "minlength") return "Please write at least a sentence.";
  if (e.kind === "maxlength") return "That's too long.";
  return "Invalid value.";
}

// Read messages (newest first). Disabled unless ADMIN_TOKEN is set.
router.get("/messages", async (req, res) => {
  const token = process.env.ADMIN_TOKEN;
  if (!token || req.get("authorization") !== `Bearer ${token}`) return res.status(401).json({ error: "Unauthorized" });
  res.json(await Message.find({}, "-__v").sort("-createdAt").limit(200).lean());
});

export default router;
