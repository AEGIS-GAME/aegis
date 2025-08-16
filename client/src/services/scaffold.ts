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
  }

  const setupAegisPath = async (): Promise<void> => {
    const path = await aegisAPI!.openAegisDirectory()
    if (path) {
      setAegisPath(path)
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
      const rawConfig = (await aegisAPI!.read_config(aegisPath)) as any
      const parsedConfig = parseClientConfig(rawConfig)
      setConfig(parsedConfig)
      return true
    } catch (error) {
      if (process.env.NODE_ENV === "development") {
        console.debug("Config loading failed:", error)
      }
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

  useEffect(() => {
    if (!aegisAPI) {
      return
    }
    if (!didInit) {
      didInit = true
      getAegisPath().then((path) => {
        setAegisPath(path)
      })

      aegisAPI.aegis_child_process.onStdout((data: string) => {
        addOutput({ content: data, has_error: false, gameIdx: 0 })
      })

      aegisAPI.aegis_child_process.onStderr((data: string) => {
        addOutput({ content: data, has_error: true, gameIdx: 0 })
      })

      aegisAPI.aegis_child_process.onExit(() => {
        aegisPid.current = undefined
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
