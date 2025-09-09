import Games from "@/core/Games"

export type WorldParams = {
  width: number
  height: number
  initialEnergy: number
  imported?: Games | null
}
