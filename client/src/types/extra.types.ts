import { ClientConfig } from "@/services"
import RingBuffer from "@/utils/ringBuffer"

export enum TabNames {
  Aegis = "Aegis",
  Game = "Game",
  Editor = "Editor",
  Settings = "Settings",
}

export enum SidebarView {
  Aegis = "Aegis",
  Game = "Game",
  Editor = "Editor",
  Settings = "Settings",
}

export enum BrushType {
  Zone = "Zone",
  Layers = "Layers",
  MoveCost = "MoveCost",
}

const shadesOfBrown = [
  [188, 104, 29],
  [171, 95, 26],
  [154, 85, 24],
  [137, 76, 21],
  [120, 67, 18],
  [111, 60, 13],
  [102, 54, 10],
  [93, 48, 7],
  [79, 40, 5],
  [65, 32, 2],
]

// Move cost 1 = lightest, move cost 10+ = darkest
export function getMoveCostColor(moveCost: number): [number, number, number, number] {
  const index = Math.min(Math.max(moveCost, 1), 10) - 1
  return [...shadesOfBrown[index], moveCost] as [number, number, number, number]
}

export type ConsoleLine = {
  has_error: boolean
  content: string
  gameIdx: number
}

export interface Scaffold {
  aegisPath: string | undefined
  setupAegisPath: () => void
  worlds: string[]
  agents: string[]
  output: RingBuffer<ConsoleLine>
  startSimulation: (
    rounds: string,
    amount: string,
    worlds: string[],
    agent: string,
    debug: boolean
  ) => void
  killSim: (() => void) | undefined
  readAegisConfig: () => Promise<boolean>
  refreshWorldsAndAgents: () => Promise<void>
  config: ClientConfig | null
  spawnError: string
  updateConfigValue: (keyPath: string, value: unknown) => Promise<boolean>
}
