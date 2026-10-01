import mongoose from "mongoose";

const messageSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true, maxlength: 100 },
    email: { type: String, required: true, trim: true, lowercase: true, maxlength: 200, match: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
    company: { type: String, trim: true, maxlength: 150 },
    message: { type: String, required: true, trim: true, minlength: 10, maxlength: 5000 },
    read: { type: Boolean, default: false },
  },
  { timestamps: true },
);

export default mongoose.model("Message", messageSchema);
