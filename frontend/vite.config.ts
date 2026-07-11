import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base './' so the built app works when served by FastAPI from any path.
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
  build: {
    outDir: "dist",
    chunkSizeWarningLimit: 1500,
  },
});
