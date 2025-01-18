import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import { createHtmlPlugin } from "vite-plugin-html";
import movePopupHtml from "./movePopupHtml"; // Import the custom plugin

export default defineConfig({
  plugins: [
    react(),
    movePopupHtml(),
    createHtmlPlugin({
      inject: {
        data: {
          title: "NimbusAI",
        },
      },
    }),

  ],
  build: {
    rollupOptions: {
      input: {
        popup: resolve(__dirname, "src/popup.html"), // Popup entry point
        dev: "src/dev.html",
        content: resolve(__dirname, "src/content.tsx"), // Content script
        background: resolve(__dirname, "src/background.tsx"), // Background script
      },
      output: {
        entryFileNames: "[name].js", // Use simple filenames like content.js
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === "popup.html") {
            return "[name].[ext]"; // Place popup.html in the root
          }
          return "assets/[name].[ext]"; // Other assets go in assets/
        },
        dir: resolve(__dirname, "dist"), // Output directory
      },
    },
  },
});
