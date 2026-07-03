import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
      "/admin": "http://localhost:8000",
    },
  },
  define: {
    __API_URL__: JSON.stringify(process.env.VITE_API_URL || "https://the-rental-shop.onrender.com"),
  },
});
