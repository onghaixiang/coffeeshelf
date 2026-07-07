import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // 127.0.0.1 (not "localhost") — on Windows, Node resolves localhost to
      // IPv6 ::1 first, but uvicorn binds IPv4, causing proxy 500s.
      "/api": "http://127.0.0.1:8000",
    },
  },
});
