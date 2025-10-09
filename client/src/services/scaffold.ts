import Game from "@/core/Game"
import Games from "@/core/Games"
import { Runner } from "@/core/Runner"
import { ClientWebSocket, aegisAPI } from "@/services"
import { useAppStore } from "@/store/useAppStore"
import { ConsoleLine, Scaffold } from "@/types"
import RingBuffer from "@/utils/ringBuffer"
import { useForceUpdate } from "@/utils/util"
import { useEffect, useRef, useState } from "react"
import invariant from "tiny-invariant"
import { ClientConfig, parseClientConfig } from "./config"

export function createScaffold(): Scaffold {
  const [aegisPath, setAegisPath] = useState<string | undefined>(undefined)
  const [spawnError, setSpawnError] = useState<string>("")
  const [worlds, setWorlds] = useState<string[]>([])
  const [agents, setAgents] = useState<string[]>([])
  const [config, setConfig] = useState<ClientConfig | null>(null)
  // const [rawConfig, setRawConfig] = useState<Record<string, unknown> | null>(null)
  const aegisPid = useRef<string | undefined>(undefined)
  const currentGameIdx = useRef(0)
  const output = useRef<RingBuffer<ConsoleLine>>(new RingBuffer(20000))
  const forceUpdate = useForceUpdate()
  let didInit = false

  const addOutput = (line: ConsoleLine): void => {
    line.gameIdx = currentGameIdx.current
    output.current.push(line)

    if (
      line.content.startsWith("[INFO][aegis]") &&
      line.content.includes("AEGIS END")
    ) {
      currentGameIdx.current++
    }

    // Only force update for error messages or when no game is running
    // This ensures startup errors are visible immediately without causing
    // excessive re-renders during normal simulation
    if (line.has_error || !Runner.games?.currentGame) {
      forceUpdate()
    }
  }

  const setupAegisPath = async (): Promise<void> => {
    const path = await aegisAPI!.openAegisDirectory()
    if (path) {
      setAegisPath(path)
      window.dispatchEvent(new CustomEvent("aegisPathSet"))
    }
  }

  const startSimulation = async (
    rounds: string,
    amount: string,
    worlds: string[],
    agent: string,
    debug: boolean
  ): Promise<void> => {
    invariant(aegisPath, "Can't find AEGIS path!")
    invariant(config, "Config not loaded. Please ensure config.yaml is valid.")

    currentGameIdx.current = 0
    output.current.clear()

    try {
      const pid = await aegisAPI!.aegis_child_process.spawn(
        rounds,
        amount,
        worlds,
        agent,
        aegisPath,
        debug
      )
      aegisPid.current = pid
      setSpawnError("")
    } catch (error) {
      setSpawnError(
        "`aegis` command not found. Please activate your virtual environment and restart the client to try again."
      )
    }
    forceUpdate()
  }

  const readAegisConfig = async (): Promise<boolean> => {
    invariant(aegisPath, "Can't find AEGIS path!")

    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const rawConfigData = (await aegisAPI!.read_config(aegisPath)) as any
      const parsedConfig = parseClientConfig(rawConfigData)
      // setRawConfig(rawConfigData)
      setConfig(parsedConfig)
      return true
    } catch (error) {
      if (process.env.NODE_ENV === "development") {
        console.debug("Config loading failed:", error)
      }
      // setRawConfig(null)
      setConfig(null)
      return false
    }
  }

  const refreshWorldsAndAgents = async (): Promise<void> => {
    invariant(aegisPath, "Can't find AEGIS path!")

    const [worldsData, agentsData] = await Promise.all([
      getWorlds(aegisPath),
      getAgents(aegisPath),
    ])

    setWorlds(worldsData)
    setAgents(agentsData)
  }

  const killSimulation = (): void => {
    invariant(aegisPid.current, "Can't kill a game if no game has started")
    aegisAPI!.aegis_child_process.kill(aegisPid.current)
    aegisPid.current = undefined
    forceUpdate()
  }

  // // Freaky way to edit specific config value while keeping orginal comments, etc.
  // const updateConfigValueInObject = (
  //   configObj: Record<string, unknown>,
  //   path: string,
  //   value: unknown
  // ): void => {
  //   const keys = path.split(".")
  //   let current: Record<string, unknown> = configObj

  //   for (let i = 0; i < keys.length - 1; i++) {
  //     if (
  //       !current[keys[i]] ||
  //       typeof current[keys[i]] !== "object" ||
  //       current[keys[i]] === null
  //     ) {
  //       current[keys[i]] = {}
  //     }
  //     current = current[keys[i]] as Record<string, unknown>
  //   }

  //   current[keys[keys.length - 1]] = value
  // }

  const updateConfigValue = async (
    keyPath: string,
    value: unknown
  ): Promise<boolean> => {
    invariant(aegisPath, "Can't find AEGIS path!")

    try {
      await aegisAPI!.update_config_value(aegisPath, keyPath, value)

      const freshConfig = await aegisAPI!.read_config(aegisPath)
      if (!freshConfig) {
        console.error("Failed to read config after update")
        return false
      }

      // setRawConfig(freshConfig)
      setConfig(parseClientConfig(freshConfig))
      return true
    } catch (error) {
      if (process.env.NODE_ENV === "development") {
        console.debug("Config update failed:", error)
      }
      return false
    }
  }

  useEffect(() => {
    if (!aegisAPI) {
      return
    }
    if (!didInit) {
      didInit = true
      getAegisPath().then((path) => {
        if (path) {
          setAegisPath(path)
          window.dispatchEvent(new CustomEvent("aegisPathSet"))
        }
      })

      aegisAPI.aegis_child_process.onStdout((data: string) => {
        addOutput({ content: data, has_error: false, gameIdx: 0 })
      })

      aegisAPI.aegis_child_process.onStderr((data: string) => {
        // console.log("Frontend received stderr:", data)
        addOutput({ content: data, has_error: true, gameIdx: 0 })
      })

      aegisAPI.aegis_child_process.onExit((exitInfo) => {
        console.log("Frontend received exit event:", exitInfo)
        aegisPid.current = undefined

        // If the process exited with an error code, add an error message to the console
        if (exitInfo.code !== null && exitInfo.code !== 0) {
          const errorMessage = exitInfo.signal
            ? `AEGIS process was terminated by signal ${exitInfo.signal}`
            : `AEGIS process exited with error code ${exitInfo.code}. This may indicate a configuration error, insufficient agents for the world spawns, or other startup issues. Check the error messages above for details.`

          console.log("Adding error message to console:", errorMessage)
          addOutput({
            content: `[ERROR] ${errorMessage}`,
            has_error: true,
            gameIdx: currentGameIdx.current,
          })
        }

        forceUpdate()
      })

      const onGamesCreated = (games: Games): void => {
        useAppStore.getState().pushToQueue(games)
        Runner.setGames(games)
      }

      const onGameCreated = (game: Game): void => {
        Runner.setGame(game)
      }
      new ClientWebSocket(onGameCreated, onGamesCreated)
    }
  }, [])

  useEffect(() => {
    if (!aegisPath) {
      return
    }

    localStorage.removeItem("aegis_agent_amount")
    localStorage.removeItem("aegis_agent")
    localStorage.removeItem("aegis_rounds")

    const loadData = async (): Promise<void> => {
      const [worldsData, agentsData] = await Promise.all([
        getWorlds(aegisPath),
        getAgents(aegisPath),
      ])

      setWorlds(worldsData)
      setAgents(agentsData)
    }

    loadData()
    localStorage.setItem("aegisPath", aegisPath)
  }, [aegisPath])

  return {
    aegisPath,
    setupAegisPath,
    worlds,
    agents,
    output: output.current,
    startSimulation,
    killSim: aegisPid.current ? killSimulation : undefined,
    readAegisConfig,
    refreshWorldsAndAgents,
    config,
    spawnError,
    updateConfigValue,
  }
}

const getAegisPath = async (): Promise<string | undefined> => {
  const localPath = localStorage.getItem("aegisPath")
  if (localPath) {
    return localPath
  }

  const fs = aegisAPI!.fs
  const path = aegisAPI!.path
  let currentDir: string = await aegisAPI!.getAppPath()

  let parentDir: string

  while (currentDir !== (parentDir = await path.dirname(currentDir))) {
    const worldsDir = await path.join(currentDir, "worlds")
    if (await fs.existsSync(worldsDir)) {
      return currentDir
    }

    currentDir = parentDir
  }

  return undefined
}

const getWorlds = async (aegisPath: string): Promise<string[]> => {
  if (!aegisAPI) {
    return []
  }

  const fs = aegisAPI.fs
  const path = aegisAPI.path

  const worldsPath = await path.join(aegisPath, "worlds")
  if (!(await fs.existsSync(worldsPath))) {
    return []
  }

  const worlds = await fs.readdirSync(worldsPath)
  const filtered_worlds = worlds
    .filter((world: string) => world.endsWith(".world"))
    .map((world: string) => world.replace(/\.world$/, ""))
  return filtered_worlds
}

const getAgents = async (aegisPath: string): Promise<string[]> => {
  if (!aegisAPI) {
    return []
  }

  const fs = aegisAPI.fs
  const path = aegisAPI.path

  const agentsPath = await path.join(aegisPath, "agents")
  if (!(await fs.existsSync(agentsPath))) {
    return []
  }

  const agentsDirs = await fs.readdirSync(agentsPath)

  // Only take the agents that have 'main.py' in their folders
  const agents: string[] = []
  for (const agent of agentsDirs) {
    const agentPath = await path.join(agentsPath, agent)
    if (!(await fs.isDirectory(agentPath))) {
      continue
    }
    const agentFiles = await fs.readdirSync(agentPath)
    if (!agentFiles.includes("main.py")) {
      continue
    }
    agents.push(agent)
  }
  return agents
}
