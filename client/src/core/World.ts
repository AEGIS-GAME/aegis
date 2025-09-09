import droneScanEyeSrc from "@/assets/drone-scan-eye.png"
import rubbleSrc from "@/assets/rubble.png"
import survivorSrcDark from "@/assets/survivor-dark.png"
import survivorSrcLight from "@/assets/survivor-light.png"
import { getMoveCostColor, Size, Vector } from "@/types"
import { THICKNESS } from "@/utils/constants"
import { getImage, renderCoords } from "@/utils/util"
import { schema } from "aegis-schema"
import invariant from "tiny-invariant"
import { EditorBrush, LayersBrush, MoveCostBrush, ZoneBrush } from "./Brushes"
import Round from "./Round"

/**
 * Represents a world in aegis.
 * @param width - Width of the world in cells.
 * @param height - Height of the world in cells.
 * @param seed - Random seed for world generation.
 * @param cells - Array of cells in the world.
 * @param startEnergy - Starting energy for agents.
 */
export default class World {
  private layerRemovals: schema.Location[] = []
  private droneScans: schema.DroneScan[] = []

  constructor(
    public readonly width: number,
    public readonly height: number,
    public readonly seed: number,
    public readonly cells: schema.Cell[],
    public readonly startEnergy: number,
    public initSpawns: schema.InitSpawn[]
  ) {}

  public applyRound(round: schema.Round | null): void {
    console.log("applyRound", round)
    this.layerRemovals = []
    this.droneScans = []

    if (!round) {
      return
    }

    for (const loc of round.layersRemoved) {
      const cell = this.cellAt(loc.x, loc.y)!
      cell.layers.shift()
      this.layerRemovals.push(loc)
    }

    for (const survHealth of round.survivorHealthUpdates) {
      const cell = this.cellAt(survHealth.location!.x, survHealth.location!.y)!
      for (const layer of cell.layers) {
        if (
          layer.object.oneofKind === "survivor" &&
          layer.object.survivor.id === survHealth.survivorId
        ) {
          layer.object.survivor.health = survHealth.newHealth
          layer.object.survivor.state = survHealth.newState
          break
        }
      }
    }

    this.droneScans = round.droneScans
  }

  /**
   * Creates a new World instance from protobuf WorldState data.
   * @param worldState - Protobuf WorldState data.
   * @returns A World instance.
   */
  public static fromSchema(world: schema.World): World {
    return new World(
      world.width,
      world.height,
      world.seed,
      world.cells,
      world.startEnergy,
      world.initSpawns
    )
  }

  /**
   * Creates a new World instance with default parameters.
   * @param width - Width of the map.
   * @param height - Height of the map.
   * @param initialEnergy - Initial energy level for agents.
   * @returns A World instance with default parameters.
   */
  static fromParams(width: number, height: number, initialEnergy: number): World {
    const cells: schema.Cell[] = Array.from({ length: width * height }, (_, index) => {
      const x = index % width
      const y = Math.floor(index / width)

      return schema.Cell.create({
        loc: { x, y },
        moveCost: 1,
        type: schema.CellType.NORMAL,
        agents: [],
        layers: [],
      })
    })

    return new World(width, height, 0, cells, initialEnergy, [])
  }

  public copy(): World {
    return new World(
      this.width,
      this.height,
      this.seed,
      this.cells.map(this.copyCell),
      this.startEnergy,
      this.initSpawns
    )
  }

  /**
   * Creates a deep copy of a Cell object.
   *
   * @param {schema.Cell} cell - The cell to copy.
   * @returns {schema.Cell} A deep copy of the input cell.
   */
  private copyCell(cell: schema.Cell): schema.Cell {
    return {
      loc: cell.loc ? { ...cell.loc } : undefined,
      moveCost: cell.moveCost,
      type: cell.type,
      agents: [...cell.agents],
      layers: cell.layers.map((layer) => ({ ...layer })),
    }
  }

  /**
   * Checks if the world map is empty.
   * A world is considered empty if:
   * - There are no spawn cells,
   * - All cells have no layers,
   * - All cells are of type "normal".
   * - All cells have a move cost of 1.
   * @returns True if the map is empty, otherwise false.
   */
  isEmpty(): boolean {
    return (
      this.getCellsByType(schema.CellType.SPAWN).length === 0 &&
      this.cells.every(
        (cell) =>
          cell.layers.length === 0 &&
          cell.type === schema.CellType.NORMAL &&
          cell.moveCost === 1
      )
    )
  }

  /**
   * Gets the size of the world map.
   * @returns An object containing the width and height of the map.
   */
  get size(): Size {
    return { width: this.width, height: this.height }
  }

  public cellAt(x: number, y: number): schema.Cell {
    return this.cells[x + y * this.width]
  }

  /**
   * Renders the map onto a canvas context.
   * @param ctx - Canvas rendering context.
   */
  draw(ctx: CanvasRenderingContext2D): void {
    ctx.strokeStyle = "black"
    ctx.lineWidth = THICKNESS

    ctx.fillStyle = "#000000"
    ctx.fillRect(0, 0, this.width, this.height)

    this.drawCells(ctx)
  }

  /**
   * Helper function to render all cells of the map.
   * @param ctx - Canvas rendering context.
   * @param thickness - Line thickness for drawing the cells.
   */
  private drawCells(ctx: CanvasRenderingContext2D): void {
    this.drawTerrain(ctx)
    this.drawSpecialCells(ctx)
  }

  /**
   * Helper function to render terrain cells of the map.
   * @param ctx - Canvas rendering context.
   * @param thickness - Line thickness for drawing the cells.
   */
  private drawTerrain(ctx: CanvasRenderingContext2D): void {
    for (let x = 0; x < this.width; x++) {
      for (let y = 0; y < this.height; y++) {
        const cell = this.cellAt(x, y)
        if (!cell) {
          continue
        }

        const [r, g, b] = getMoveCostColor(cell.moveCost)
        ctx.fillStyle = `rgba(${r}, ${g}, ${b})`

        const coords = renderCoords(x, y, this.size)
        ctx.fillRect(
          coords.x + THICKNESS / 2,
          coords.y + THICKNESS / 2,
          1 - THICKNESS,
          1 - THICKNESS
        )
      }
    }
  }

  /**
   * Helper function to render special cells like charging, fire, and killer cells.
   * @param ctx - Canvas rendering context.
   */
  private drawSpecialCells(ctx: CanvasRenderingContext2D): void {
    for (const cell of this.cells) {
      if (!cell.loc) {
        continue
      }
      const { x, y } = cell.loc

      const coords = renderCoords(x, y, this.size)

      if (cell.type === schema.CellType.NORMAL) {
        continue
      }

      if (cell.type === schema.CellType.CHARGING) {
        ctx.fillStyle = "#3f00ff"
      } else if (cell.type === schema.CellType.KILLER) {
        ctx.fillStyle = "#cc0000"
      } else if (cell.type === schema.CellType.SPAWN) {
        this.drawSpawn(ctx, coords)
        continue
      }

      ctx.fillRect(
        coords.x + THICKNESS / 2,
        coords.y + THICKNESS / 2,
        1 - THICKNESS,
        1 - THICKNESS
      )
    }
  }

  /**
   * Helper function to render spawn zones on the map.
   * @param ctx - Canvas rendering context.
   */
  private drawSpawn(ctx: CanvasRenderingContext2D, coords: Vector): void {
    ctx.save()

    ctx.beginPath()
    ctx.rect(coords.x, coords.y, 1, 1)
    ctx.clip()

    const stripeWidth = 0.125
    const numStripes = 8

    for (let i = -numStripes; i < numStripes * 2; i++) {
      ctx.beginPath()
      ctx.fillStyle = i % 2 === 0 ? "#ffff00" : "#000000"

      const startPointX = coords.x + i * stripeWidth
      const endPointX = startPointX + stripeWidth

      ctx.beginPath()
      ctx.moveTo(startPointX, coords.y)
      ctx.lineTo(endPointX, coords.y)
      ctx.lineTo(endPointX - 1, coords.y + 1)
      ctx.lineTo(startPointX - 1, coords.y + 1)
      ctx.closePath()
      ctx.fill()
    }
    ctx.restore()
  }

  public drawLayers(ctx: CanvasRenderingContext2D, full: boolean): void {
    const lightSurv = getImage(survivorSrcLight)
    const darkSurv = getImage(survivorSrcDark)
    const rubble = getImage(rubbleSrc)
    invariant(lightSurv && darkSurv && rubble, "layer images should be loaded already")

    const locs = full ? this.getAllLocations() : this.layerRemovals

    for (const loc of locs) {
      const x = loc.x
      const y = loc.y

      const coords = renderCoords(x, y, this.size)
      ctx.clearRect(coords.x, coords.y, 1, 1)

      const layers = this.cellAt(x, y).layers
      if (!layers.length) {
        continue
      }

      const survivorCount = this.countByKind(layers, "survivor")
      const rubbleCount = this.countByKind(layers, "rubble")

      const topLayer = layers[0]
      const kind = topLayer.object.oneofKind
      const [, , , moveCost] = getMoveCostColor(this.cellAt(x, y).moveCost)

      if (kind === "survivor") {
        if (moveCost <= 5) {
          ctx.drawImage(darkSurv, coords.x, coords.y, 1, 1)
        } else {
          ctx.drawImage(lightSurv, coords.x, coords.y, 1, 1)
        }
      } else if (kind === "rubble") {
        ctx.drawImage(rubble, coords.x + 0.025, coords.y + 0.025, 0.95, 0.95)
      }

      ctx.font = "0.3px monospace"
      ctx.textBaseline = "bottom"

      if (survivorCount > 0) {
        ctx.textAlign = "right"
        if (moveCost <= 5) {
          ctx.fillStyle = "#0919ff"
        } else {
          ctx.fillStyle = "#0f8cff"
        }
        ctx.fillText(String(survivorCount), coords.x + 0.97, coords.y + 1.01)
      }

      if (rubbleCount > 0) {
        ctx.fillStyle = "#444444"
        ctx.textAlign = "left"
        ctx.fillText(String(rubbleCount), coords.x + 0.03, coords.y + 1.01)
      }
    }
  }

  public drawDroneScans(ctx: CanvasRenderingContext2D): void {
    const droneScanEye = getImage(droneScanEyeSrc)
    invariant(droneScanEye, "drone scan eye image should be loaded already")

    for (const droneScan of this.droneScans) {
      const coords = renderCoords(
        droneScan.location!.x,
        droneScan.location!.y,
        this.size
      )

      ctx.save()
      ctx.globalAlpha = 0.5
      ctx.drawImage(droneScanEye, coords.x, coords.y, 1, 1)
      ctx.restore()
    }
  }

  public getBrushes(round: Round): EditorBrush[] {
    return [new ZoneBrush(round), new MoveCostBrush(round), new LayersBrush(round)]
  }

  public getDroneScans(): schema.DroneScan[] {
    return this.droneScans
  }

  public applyDroneScanUpdate(droneScanUpdate: schema.DroneScanUpdate): void {
    this.droneScans = droneScanUpdate.droneScans
  }

  public getCellsByType(type: schema.CellType): schema.Cell[] {
    return this.cells.filter((cell) => cell.type === type)
  }

  private countByKind(layers: schema.WorldObject[], kind: string): number {
    return layers.filter((layer) => layer.object.oneofKind === kind).length
  }

  private getAllLocations(): schema.Location[] {
    const locs: schema.Location[] = []
    const { width, height } = this.size
    for (let x = 0; x < width; x++) {
      for (let y = 0; y < height; y++) {
        locs.push({ x, y })
      }
    }
    return locs
  }
}
