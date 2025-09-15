/* eslint-disable @typescript-eslint/no-explicit-any */
type AegisAPI = {
  openAegisDirectory: () => Promise<string | undefined>
  getAppPath: () => Promise<string>
  getAppVersion: () => Promise<string>
  getClientVersion: (aegisPath: string) => Promise<string | null>
  openExternal: (url: string) => Promise<void>
  exportWorld: (name: string, world: Uint8Array) => Promise<void>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  read_config: (aegisPath: string) => Promise<any>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  update_config_value: (aegisPath: string, keyPath: string, value: any) => Promise<void>
  path: {
    join: (...args: string[]) => Promise<string>
    dirname: (dir: string) => Promise<string>
  }
  fs: {
    existsSync: (arg: string) => Promise<boolean>
    readdirSync: (arg: string) => Promise<string[]>
    readFileSync: (arg: string) => Promise<string>
    writeFileSync: (path: string, data: string) => Promise<void>
    isDirectory: (arg: string) => Promise<boolean>
  }
  aegis_child_process: {
    spawn: (
      rounds: string,
      amount: string,
      world: string[],
      agent: string,
      aegisPath: string,
      debug: boolean
    ) => Promise<string>
    kill: (aegisPid: string) => void
    onStdout: (callback: (data: string) => void) => void
    onStderr: (callback: (data: string) => void) => void
    onExit: (
      callback: (exitInfo: { code: number | null; signal: string | null }) => void
    ) => void
  }
}

let aegisAPI: AegisAPI | undefined = undefined

if ((window as any).electronAPI) {
  aegisAPI = (window as any).electronAPI as AegisAPI
}

export { aegisAPI }
