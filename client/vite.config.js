import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const api = "http://localhost:" + (process.env.API_PORT || 5000);

export default defineConfig({
  plugins: [react()],
  // "/assets" is the repo's image folder (served by Express), so keep the bundle apart
  build: { assetsDir: "static" },
  server: {
    port: 5173,
    proxy: { "/api": api, "/assets": api },
  },
});
