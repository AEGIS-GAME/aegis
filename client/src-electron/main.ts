import { is } from "@electron-toolkit/utils"
import child_process from "child_process"
import { app, BrowserWindow, dialog, ipcMain, shell } from "electron"
import fs from "fs"
import path from "path"
import yaml from "yaml"

class ElectronApp {
  private mainWindow: BrowserWindow | null = null
  private processes = new Map<string, child_process.ChildProcess>()

  constructor() {
    this.initialize()
  }

  private initialize(): void {
    app.whenReady().then(() => {
      this.createWindow()
      this.setupAppLifecycleHandlers()
      this.setupIpcHandlers()
    })
  }

  private createWindow(): void {
    const version = app.getVersion()
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      autoHideMenuBar: true,
      title: `AEGIS v${version}`,
      webPreferences: {
        devTools: is.dev,
        preload: path.join(__dirname, "../preload/index.js"),
      },
    })

    const URL = is.dev
      ? "http://localhost:5173"
      : `file://${path.join(__dirname, "../renderer/index.html")}`

    this.mainWindow.loadURL(URL)
    this.mainWindow.once("ready-to-show", () => this.mainWindow?.show())
    this.mainWindow.on("closed", () => {
      this.mainWindow = null
    })
  }

  private setupAppLifecycleHandlers(): void {
    app.on("activate", () => {
      if (this.mainWindow === null) {
        this.createWindow()
      }
    })

    app.on("before-quit", () => this.killAllProcesses())

    app.on("window-all-closed", () => {
      if (process.platform !== "darwin") {
        app.quit()
      }
    })
  }

  private setupIpcHandlers(): void {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ipcMain.handle("electronAPI", async (_, command: string, ...args: any[]) => {
      return this.handleElectronAPI(command, ...args)
    })

    ipcMain.handle("aegis_child_process.spawn", async (_, ...args) => {
      return await this.spawnAegisProcess(
        args[0], // rounds
        args[1], // amount
        args[2], // world
        args[3], // agent
        args[4], // aegis path
        args[5] // debug
      )
    })

    ipcMain.handle("aegis_child_process.kill", async (_, pid) => {
      this.killProcess(pid)
    })

    ipcMain.handle("read_config", async (_, aegisPath) => this.readConfig(aegisPath))
    ipcMain.handle("update_config_value", async (_, aegisPath, keyPath, value) =>
      this.updateConfigValue(aegisPath, keyPath, value)
    )
  }

  private killAllProcesses(): void {
    for (const [pid, process] of this.processes) {
      process.kill()
      this.processes.delete(pid)
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private async handleElectronAPI(command: string, ...args: any[]): Promise<any> {
    switch (command) {
      case "openAegisDirectory":
        return this.openAegisDirectory()
      case "getAppPath":
        return app.getAppPath()
      case "getAppVersion":
        return app.getVersion()
      case "getClientVersion":
        return this.getClientVersion(args[0])
      case "openExternal":
        return shell.openExternal(args[0])
      case "path.join":
        return path.join(...args)
      case "path.dirname":
        return path.dirname(args[0])
      case "fs.existsSync":
        return fs.existsSync(args[0])
      case "fs.readdirSync":
        return fs.readdirSync(args[0])
      case "fs.isDirectory":
        return fs.statSync(args[0]).isDirectory()
      case "fs.readFileSync":
        return fs.readFileSync(args[0], "utf8")
      case "fs.writeFileSync":
        return fs.writeFileSync(args[0], args[1])
      case "exportWorld":
        return this.exportWorld(args[0], args[1])
      case "aegis_child_process.spawn":
        return this.spawnAegisProcess(
          args[0], // rounds
          args[1], // amount
          args[2], // world
          args[3], // agent
          args[4], // aegis path
          args[5] // debug
        )
      case "aegis_child_process.kill":
        return this.killProcess(args[0])
    }
  }

  private async openAegisDirectory(): Promise<string | undefined> {
    const result = await dialog.showOpenDialog({
      properties: ["openDirectory"],
      title: "Select Aegis directory",
    })
    return result.canceled ? undefined : result.filePaths[0]
  }

  private async exportWorld(defaultPath: string, content: string): Promise<void> {
    const exportResult = await dialog.showSaveDialog({
      defaultPath,
      title: "Export World",
    })
    if (!exportResult.canceled && exportResult.filePath) {
      fs.writeFileSync(exportResult.filePath, content)
    }
  }

  // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
  private readConfig(aegisPath: string) {
    try {
      const configPath = path.join(aegisPath, "config", "config.yaml")
      const fileContent = fs.readFileSync(configPath, "utf8")
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return yaml.parse(fileContent) as Record<string, any>
    } catch (error) {
      console.error(`Error reading the config file: ${error}`)
      return null
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private updateConfigValue(aegisPath: string, keyPath: string, value: any): void {
    const configPath = path.join(aegisPath, "config", "config.yaml")

    try {
      const fileContent = fs.readFileSync(configPath, "utf8")
      const config = yaml.parse(fileContent)

      if (!config) {
        throw new Error("Failed to parse config file")
      }

      // Validate key path exists in config
      const keys = keyPath.split(".")
      let current = config
      for (const key of keys) {
        if (current?.[key] === undefined) {
          throw new Error(`Key path '${keyPath}' not found in config`)
        }
        current = current[key]
      }

      // Create regex to match key: value (with comments)
      const keyName = keys[keys.length - 1]
      const escapedKey = keyName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
      const regex = new RegExp(`^(\\s*)${escapedKey}\\s*:\\s*(.*?)(\\s*#.*)?$`, "gm")
      const newValue = typeof value === "string" ? `"${value}"` : value
      const replacement = `$1${keyName}: ${newValue}$3`

      const updatedContent = fileContent.replace(regex, replacement)

      if (updatedContent === fileContent) {
        throw new Error(`Key '${keyName}' not found in file`)
      }

      fs.writeFileSync(configPath, updatedContent, "utf8")
    } catch (error) {
      console.error(`Error updating config value: ${error}`)
      throw error
    }
  }

  private spawnAegisProcess(
    rounds: string,
    amount: string,
    world: string[],
    agent: string,
    aegisPath: string,
    debug: boolean
  ): Promise<string> {
    const procArgs = [
      "launch",
      "--amount",
      amount,
      "--agent",
      `${agent}`,
      "--world",
      ...world,
      "--rounds",
      rounds,
      "--client",
      ...(debug ? ["--debug"] : []),
    ]

    const venvPath = this.findVenvPython(aegisPath)

    if (!venvPath) {
      throw new Error("Virtual environment not found")
    }

    const aegisExec =
      process.platform === "win32"
        ? path.join(venvPath, "aegis.exe")
        : path.join(venvPath, "aegis")

    const childAegis = child_process.spawn(aegisExec, procArgs, {
      cwd: aegisPath,
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
      stdio: ["pipe", "pipe", "pipe"],
    })

    return new Promise((resolve, reject) => {
      childAegis.on("error", (error) => {
        console.error("Aegis process error:", error)
        reject(error)
      })
      childAegis.on("spawn", () => {
        const pid = childAegis.pid?.toString()
        if (pid) {
          this.processes.set(pid, childAegis)

          let stdoutBuffer = ""
          let stderrBuffer = ""

          childAegis.stdout?.on("data", (data) => {
            const { lines, buffer } = this.flushBuffer(stdoutBuffer, data.toString())
            stdoutBuffer = buffer
            lines.forEach((line) => {
              this.mainWindow?.webContents.send("aegis_child_process.stdout", line)
            })
          })

          childAegis.stderr?.on("data", (data) => {
            const { lines, buffer } = this.flushBuffer(stderrBuffer, data.toString())
            stderrBuffer = buffer
            lines.forEach((line) => {
              this.mainWindow?.webContents.send("aegis_child_process.stderr", line)
            })
          })

          childAegis.on("exit", (code, signal) => {
            if (stdoutBuffer.trim()) {
              this.mainWindow?.webContents.send(
                "aegis_child_process.stdout",
                stdoutBuffer.trim()
              )
            }
            if (stderrBuffer.trim()) {
              this.mainWindow?.webContents.send(
                "aegis_child_process.stderr",
                stderrBuffer.trim()
              )
            }

            this.processes.delete(pid)
            this.mainWindow?.webContents.send("aegis_child_process.exit", {
              code,
              signal,
            })
          })

          resolve(pid)
        }
      })
    })
  }

  private flushBuffer(
    buffer: string,
    data: string
  ): { lines: string[]; buffer: string } {
    const combined = buffer + data
    const lines = combined.split("\n")
    const newBuffer = lines.pop() ?? ""

    const validLines = lines.filter((line) => line.trim().length > 0)

    return { lines: validLines, buffer: newBuffer }
  }

  private killProcess(pid: string): void {
    const process = this.processes.get(pid)
    if (process) {
      process.kill()
      this.processes.delete(pid)
    }
  }

  private findVenvPython(aegisPath: string): string | null {
    const isWindows = process.platform === "win32"
    const venvPath = isWindows
      ? path.join(aegisPath, ".venv", "Scripts")
      : path.join(aegisPath, ".venv", "bin")
    return fs.existsSync(venvPath) ? venvPath : null
  }

  private getClientVersion(aegisPath: string): string | null {
    try {
      if (!aegisPath) {
        return null
      }

      const versionFile = path.join(aegisPath, "client", "client-version.txt")
      if (fs.existsSync(versionFile)) {
        const version = fs.readFileSync(versionFile, "utf8").trim()
        return version || null
      }

      // Fallback to package.json for development
      const packageJsonPath = path.join(aegisPath, "client", "package.json")
      if (fs.existsSync(packageJsonPath)) {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"))
        return packageJson.version || null
      }

      return null
    } catch (error) {
      console.error("Error reading client version:", error)
      return null
    }
  }
}

new ElectronApp()
