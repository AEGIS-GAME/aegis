import { schema } from "aegis-schema"

export enum CanvasLayers {
  Background,
  Layers,
  Agent,
  DroneScan,
}

export type Size = {
  width: number
  height: number
}

export type Vector = {
  x: number
  y: number
}

export type Arguments =
  | "energy_level"
  | "number_of_survivors"
  | "energy_required"
  | "agents_required"

export type Rubble = {
  energy_required: number
  agents_required: number
}

export type Survivor = {
  energy_level: number
}

export interface WorldData {
  world_info: {
    size: Size
    seed: number
    start_energy: number
  }
  cells: schema.Cell[]
}
