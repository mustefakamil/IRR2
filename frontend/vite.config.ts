import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

// Everything is inlined into one self-contained index.html (viteSingleFile),
// so the deployed app is a single request — robust on flaky/cold-start hosting.
export default defineConfig({
  plugins: [react(), viteSingleFile()],
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
