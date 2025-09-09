import Agents from "@/core/Agents"
import Game from "@/core/Game"
import Games from "@/core/Games"
import Round from "@/core/Round"
import World from "@/core/World"
import { aegisAPI } from "@/services"
import { schema } from "aegis-schema"
import invariant from "tiny-invariant"

class WorldValidator {
  static validate(world: World): string {
    if (world.getCellsByType(schema.CellType.SPAWN).length === 0) {
      return "Missing spawn zones!"
    }

    if (!this.hasSurvivors(world)) {
      return "Missing at least 1 survivor!"
    }

    // This case should be impossible, but you never know
    const moveCostError = this.verifyMoveCosts(world)
    if (moveCostError) {
      return moveCostError
    }

    return ""
  }

  private static hasSurvivors(world: World): boolean {
    return world.cells.some((cell) =>
      cell.layers.some((layer) => layer.object.oneofKind === "survivor")
    )
  }

  private static verifyMoveCosts(world: World): string | null {
    for (const cell of world.cells) {
      if (cell.type !== schema.CellType.NORMAL && cell.moveCost !== 1) {
        const x = cell.loc!.x
        const y = cell.loc!.y
        return `Cell at (${x}, ${y}) has move cost ${cell.moveCost}, expected 1`
      }
    }
    return null
  }
}

export async function importWorld(file: File): Promise<Games> {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.readAsArrayBuffer(file)
    reader.onload = (): void => {
      const binary = new Uint8Array(reader.result as ArrayBuffer)
      const proto_world = schema.World.fromBinary(binary)
      const world = World.fromSchema(proto_world)
      const games = new Games(false)
      const agents = new Agents(games)
      const game = new Game(games, world, agents)
      games.currentGame = game
      resolve(games)
    }
  })
}

export async function exportWorld(
  round: Round,
  worldName: string
): Promise<string | null> {
  const world = round.world
  const validationError = WorldValidator.validate(world)
  if (validationError) {
    return validationError
  }

  try {
    const protoWorld = schema.World.create({
      width: world.size.width,
      height: world.size.height,
      seed: Math.floor(Math.random() * 10000),
      startEnergy: world.startEnergy,
      cells: world.cells,
      initSpawns: world.initSpawns,
    })
    const binary = schema.World.toBinary(protoWorld)

    const aegisPath = localStorage.getItem("aegisPath")
    invariant(aegisPath, "Aegis path not found in localStorage")

    const fullName = `${worldName}.world`
    const fullPath = await aegisAPI.path.join(aegisPath, "worlds", fullName)

    await aegisAPI.exportWorld(fullPath, binary)
    return null
  } catch (error) {
    // @ts-ignore: error
    return `Error exporting world: ${error.message}`
  }
}
