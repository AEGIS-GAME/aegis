import { CanvasLayers, Size, Vector } from "@/types"
import { TILE_SIZE } from "@/utils/constants"
import { loadImage, renderCoords } from "@/utils/util"
import { ListenerKey, notify } from "./Listeners"
import { Runner } from "./Runner"

import droneScanEye from "@/assets/drone-scan-eye.png"
import goobA from "@/assets/goob-team-a.png"
import goobB from "@/assets/goob-team-b.png"
import rubble from "@/assets/rubble.png"
import darkSurvivor from "@/assets/survivor-dark.png"
import lightSurvivor from "@/assets/survivor-light.png"

class RendererClass {
  private canvases: Record<keyof typeof CanvasLayers, HTMLCanvasElement> = {} as Record<
    keyof typeof CanvasLayers,
    HTMLCanvasElement
  >
  private fullRedraw = false
  private mouseDownClick: boolean = false
  private mouseDownRight: boolean = false
  private selectedTile: Vector | undefined = undefined
  private hoveredTile: Vector | undefined = undefined
  private layerViewerTile: Vector | undefined = undefined

  constructor() {
    const numericLayers = Object.values(CanvasLayers).filter(
      (value) => typeof value === "number"
    ) as number[]
    numericLayers.forEach((layerValue, index) => {
      const canvas = document.createElement("canvas")
      canvas.style.zIndex = (index + 1).toString()
      canvas.style.position = "absolute"
      canvas.style.top = "50%"
      canvas.style.left = "50%"
      canvas.style.maxWidth = "100%"
      canvas.style.maxHeight = "100%"
      canvas.style.transform = "translate(-50%, -50%)"
      const layerKey = CanvasLayers[layerValue] as keyof typeof CanvasLayers
      this.canvases[layerKey] = canvas
    })
    const canvasArray = Object.values(this.canvases)
    const topCanvas = canvasArray[canvasArray.length - 1]
    topCanvas.onmousedown = (e): void => this.mouseDown(e)
    topCanvas.onmouseup = (e): void => this.mouseUp(e)
    topCanvas.onmousemove = (e): void => this.mouseMove(e)
    topCanvas.onclick = (e): void => this.click(e)
    topCanvas.onmouseleave = (): void => this.mouseLeave()

    loadImage(goobA)
    loadImage(goobB)
    loadImage(lightSurvivor)
    loadImage(darkSurvivor)
    loadImage(rubble)
    loadImage(droneScanEye)
  }

  renderToContainer(container: HTMLDivElement | null): void {
    if (!container) {
      return
    }
    Object.values(this.canvases).forEach((canvas) => {
      container.appendChild(canvas)
    })
  }

  doFullRedraw(): void {
    this.fullRedraw = true
  }

  ctx(layer: CanvasLayers): CanvasRenderingContext2D | null {
    const canvas = this.canvases[CanvasLayers[layer] as keyof typeof CanvasLayers]
    return canvas.getContext("2d")
  }

  fullRender(): void {
    const ctx = this.ctx(CanvasLayers.Background)
    const game = Runner.game
    if (!ctx || !game) {
      return
    }
    game.currentRound.world.draw(ctx)
    this.render()
  }

  render(): void {
    const actx = this.ctx(CanvasLayers.Agent)
    const lctx = this.ctx(CanvasLayers.Layers)
    const dctx = this.ctx(CanvasLayers.DroneScan)
    const game = Runner.game
    if (!actx || !lctx || !dctx || !game) {
      return
    }

    const round = game.currentRound
    actx.clearRect(0, 0, actx.canvas.width, actx.canvas.height)
    round.agents.draw(game, actx)

    const full = this.fullRedraw
    this.fullRedraw = false
    round.world.drawLayers(lctx, full)
    round.world.drawDroneScans(lctx)
  }

  onGameChange(): void {
    const game = Runner.game
    if (!game) {
      return
    }
    this.fullRedraw = true
    this.updateCanvasSize(game.world.size)
    this.selectedTile = undefined
    this.hoveredTile = undefined
    notify(ListenerKey.Canvas)
    notify(ListenerKey.Hover)
    this.fullRender()
  }

  private updateCanvasSize(size: Size): void {
    Object.values(this.canvases).forEach((canvas) => {
      const ctx = canvas.getContext("2d")
      if (!ctx) {
        return
      }
      ctx.setTransform(1, 0, 0, 1, 0, 0)
      canvas.width = size.width * TILE_SIZE
      canvas.height = size.height * TILE_SIZE
      ctx.scale(TILE_SIZE, TILE_SIZE)
    })
  }

  private mouseDown(e: MouseEvent): void {
    this.mouseDownClick = true
    if (e.button === 2) {
      this.mouseDownRight = true
    }
    notify(ListenerKey.Canvas)
  }

  private mouseUp(e: MouseEvent): void {
    this.mouseDownClick = false
    if (e.button === 2) {
      this.mouseDownRight = false
    }
    notify(ListenerKey.Canvas)
  }

  private mouseMove(e: MouseEvent): void {
    const tile = this.eventToPoint(e)
    if (!tile || (tile.x === this.hoveredTile?.x && tile.y === this.hoveredTile.y)) {
      return
    }
    this.hoveredTile = tile
    this.updateCursorForHover()
    notify(ListenerKey.Hover)
  }

  private click(e: MouseEvent): void {
    this.selectedTile = this.eventToPoint(e)
    if (!this.selectedTile) {
      return
    }
    notify(ListenerKey.Canvas)

    if (Runner.games?.playable) {
      this.layerViewerTile = this.selectedTile
      notify(ListenerKey.LayerViewer)
    }
  }

  private mouseLeave(): void {
    this.mouseDownClick = false
    this.mouseDownRight = false
    this.hoveredTile = undefined
    this.updateCursorForHover()
    notify(ListenerKey.Hover)
  }

  public getMouseDownClick(): boolean {
    return this.mouseDownClick
  }

  public getMouseDownRight(): boolean {
    return this.mouseDownRight
  }

  public getSelectedTile(): Vector | undefined {
    return this.selectedTile
  }

  public getHoveredTile(): Vector | undefined {
    return this.hoveredTile
  }

  public getLayerViewerTile(): Vector | undefined {
    return this.layerViewerTile
  }

  private eventToPoint(e: MouseEvent): Vector | undefined {
    const canvas = e.target as HTMLCanvasElement
    const rect = canvas.getBoundingClientRect()
    const world = Runner.game?.world
    if (!world) {
      return undefined
    }

    const normX = (e.clientX - rect.left) / rect.width
    const normY = (e.clientY - rect.top) / rect.height
    const { width, height } = world.size

    const xx = Math.floor(normX * width)
    const yy = Math.floor(normY * height)
    const { x, y } = renderCoords(xx, yy, world.size)

    if (x < 0 || y < 0 || x >= width || y >= height) {
      return undefined
    }

    return { x, y }
  }

  public updateCursorForHover(): void {
    const canvasArray = Object.values(this.canvases)
    const topCanvas = canvasArray[canvasArray.length - 1]

    const isSimulationRunning = Runner.games?.playable
    const isHoveringCell = this.hoveredTile !== undefined

    if (isSimulationRunning && isHoveringCell) {
      topCanvas.style.cursor = "pointer"
    } else {
      topCanvas.style.cursor = "default"
    }
  }
}

export const Renderer = new RendererClass()
