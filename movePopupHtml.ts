import { Plugin } from "vite";
import { promises as fs } from "fs";
import { resolve } from "path";

export default function movePopupHtml(): Plugin {
  return {
    name: "move-popup-html",
    async writeBundle() {
      const srcPath = resolve(__dirname, "dist/src/popup.html");
      const destPath = resolve(__dirname, "dist/popup.html");
      const srcDir = resolve(__dirname, "dist/src");

      try {
        // Check if the source file exists
        await fs.access(srcPath);

        // Move the file to the root of `dist/`
        await fs.rename(srcPath, destPath);

        // Remove the now-empty `dist/src` directory
        await fs.rm(srcDir, { recursive: true, force: true });

        console.log("Moved popup.html to root of dist/ and cleaned up dist/src/");
      } catch (err) {
        console.error("Error moving popup.html:", err);
      }
    },
  };
}
