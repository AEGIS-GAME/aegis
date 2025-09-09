import path from "path"
import { defineConfig, externalizeDepsPlugin } from "electron-vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  main: {
    build: {
      rollupOptions: {
        input: {
          index: path.resolve(__dirname, "src-electron/main.ts"),
        },
        output: {
          manualChunks(id) {
            if (id.includes("node_modules")) {
              return id.toString().split("node_modules/")[1].split("/")[0].toString()
            }
          },
        },
      },
      outDir: "dist/main",
    },
    plugins: [externalizeDepsPlugin()],
  },
  preload: {
    build: {
      rollupOptions: {
        input: {
          index: path.resolve(__dirname, "src-electron/preload.ts"),
        },
        output: {
          manualChunks(id) {
            if (id.includes("node_modules")) {
              return id.toString().split("node_modules/")[1].split("/")[0].toString()
            }
          },
        },
      },
      outDir: "dist/preload",
    },
    plugins: [externalizeDepsPlugin()],
  },
  renderer: {
    root: ".",
    build: {
      rollupOptions: {
        input: {
          index: path.resolve(__dirname, "index.html"),
        },
        output: {
          manualChunks(id) {
            if (id.includes("node_modules")) {
              return id.toString().split("node_modules/")[1].split("/")[0].toString()
            }
          },
        },
      },
      outDir: "dist/renderer",
    },
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
  },
})
