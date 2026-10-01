import mongoose from "mongoose";

const image = new mongoose.Schema(
  {
    src: { type: String, required: true },
    caption: { type: String, required: true },
    alt: { type: String, required: true },
    width: Number,
    height: Number,
    kind: { type: String, enum: ["photo", "diagram"], default: "photo" },
  },
  { _id: false },
);

const fact = new mongoose.Schema({ label: String, value: String }, { _id: false });

const projectSchema = new mongoose.Schema(
  {
    slug: { type: String, required: true, unique: true },
    order: { type: Number, required: true },
    type: { type: String, required: true, enum: ["independent", "professional"] },
    context: { type: String, required: true },
    year: String,
    name: { type: String, required: true },
    tagline: String,
    facts: [fact],
    highlights: [String],
    skills: [String],
    cover: image,
    images: [image],
  },
  { timestamps: true },
);

export default mongoose.model("Project", projectSchema);
