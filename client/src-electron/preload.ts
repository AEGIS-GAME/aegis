/* eslint-disable */
import { contextBridge, ipcRenderer } from "electron"

const invoke = (command: string, ...args: any[]) => {
  return new Promise(async (resolve, reject) => {
    try {
      const result = await ipcRenderer.invoke("electronAPI", command, ...args)
      resolve(result)
    } catch (error) {
      reject(resolve)
    }
  })
}

const electronAPI = {
  openAegisDirectory: () => invoke("openAegisDirectory"),
  getAppPath: (...args: any[]) => invoke("getAppPath", ...args),
  getAppVersion: () => invoke("getAppVersion"),
  getClientVersion: (aegisPath: string) => invoke("getClientVersion", aegisPath),
  openExternal: (url: string) => invoke("openExternal", url),
  exportWorld: (...args: any[]) => invoke("exportWorld", ...args),
  read_config: (aegisPath: string) => ipcRenderer.invoke("read_config", aegisPath),
  update_config_value: (aegisPath: string, keyPath: string, value: any) =>
    ipcRenderer.invoke("update_config_value", aegisPath, keyPath, value),
  path: {
    join: (...args: any[]) => invoke("path.join", ...args),
    dirname: (...args: any[]) => invoke("path.dirname", ...args),
  },
  fs: {
    existsSync: (...args: any[]) => invoke("fs.existsSync", ...args),
    readdirSync: (...args: any[]) => invoke("fs.readdirSync", ...args),
    readFileSync: (...args: any[]) => invoke("fs.readFileSync", ...args),
    writeFileSync: (...args: any[]) => invoke("fs.writeFileSync", ...args),
    isDirectory: (...args: any[]) => invoke("fs.isDirectory", ...args),
  },
  aegis_child_process: {
    spawn: (
      rounds: string,
      amount: string,
      world: string[],
      agent: string,
      aegisPath: string,
      debug: boolean
    ) =>
      ipcRenderer.invoke(
        "aegis_child_process.spawn",
        rounds,
        amount,
        world,
        agent,
        aegisPath,
        debug
      ),
    kill: (pid: string) => ipcRenderer.invoke("aegis_child_process.kill", pid),
    onStdout: (callback: (data: string) => void) =>
      ipcRenderer.on("aegis_child_process.stdout", (_, data) => callback(data)),
    onStderr: (callback: (data: string) => void) =>
      ipcRenderer.on("aegis_child_process.stderr", (_, data) => callback(data)),
    onExit: (
      callback: (exitInfo: { code: number | null; signal: string | null }) => void
    ) =>
      ipcRenderer.on("aegis_child_process.exit", (_, exitInfo) => callback(exitInfo)),
  },
}

contextBridge.exposeInMainWorld("electronAPI", electronAPI)
