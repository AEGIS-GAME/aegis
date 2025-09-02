import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Agents from "@/core/Agents"
import { EditorBrush } from "@/core/Brushes"
import Game from "@/core/Game"
import Games from "@/core/Games"
import { ListenerKey, notify } from "@/core/Listeners"
import { Renderer } from "@/core/Renderer"
import { Runner } from "@/core/Runner"
import World from "@/core/World"
import useCanvas from "@/hooks/useCanvas"
import useHover from "@/hooks/useHover"
import useRound from "@/hooks/useRound"
import { cn } from "@/lib/utils"
import { useAppStore } from "@/store/useAppStore"
import { Scaffold, Vector, WorldParams } from "@/types"
import { MAP_MAX, MAP_MIN } from "@/utils/constants"
import { Upload } from "lucide-react"
import { useEffect, useMemo, useRef, useState } from "react"
import ConfirmClearDialog from "../ConfirmClearDialog"
import LayerEditor from "../dnd/LayerEditor"
import ExportDialog from "../ExportDialog"
import NumberInput from "../NumberInput"
import { Button } from "../ui/button"
import { Label } from "../ui/label"
import Brush from "./Brush"
import { exportWorld, importWorld } from "./MapGenerator"

export default function Editor({
  isOpen,
  scaffold,
}: {
  isOpen: boolean
  scaffold: Scaffold
}): JSX.Element | null {
  const round = useRound()
  const hoveredTile = useHover()
  const { rightClick, mouseDown } = useCanvas()
  const [brushes, setBrushes] = useState<EditorBrush[]>([])
  const [worldParams, setWorldParams] = useState<WorldParams>({
    width: 15,
    height: 15,
    initialEnergy: 100,
  })
  const [isWorldEmpty, setIsWorldEmpty] = useState<boolean>(true)
  const [isEditorOpen, setIsEditorOpen] = useState<boolean>(false)
  const [selectedTile, setSelectedTile] = useState<Vector | undefined>(undefined)

  const editorGames = useAppStore((state) => state.editorGames)
  const setEditorGames = useAppStore((state) => state.setEditorGames)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    if (!isOpen) {
      Runner.setGames(undefined)
      return
    }

    let games = editorGames

    if (worldParams.imported) {
      games = worldParams.imported
    } else if (!games || worldParams.imported === null) {
      games = createNewEditorGames(worldParams)
    }

    if (!games) {
      return
    }

    setEditorGames(games)
    Runner.setGame(games.currentGame!)

    const round = games.currentGame!.currentRound
    const world = round.world

    // check so it doesnt get stuck in a render loop
    if (
      world.size.width !== worldParams.width ||
      world.size.height !== worldParams.height ||
      world.startEnergy !== worldParams.initialEnergy
    ) {
      setWorldParams((prev) => ({
        ...prev,
        width: world.size.width,
        height: world.size.height,
        initialEnergy: world.startEnergy,
      }))
    }

    const loadedBrushes = world.getBrushes(round)
    loadedBrushes[0].open = true
    setBrushes(loadedBrushes)
    setIsWorldEmpty(world.isEmpty())
    if (worldParams.imported) {
      setWorldParams((prev) => ({ ...prev, imported: undefined }))
    }
  }, [isOpen, worldParams])

  const worldEmpty = (): boolean => !round || round.world.isEmpty()
  const currentBrush = brushes.find((b) => b.open)

  const clearWorld = (): void => {
    setEditorGames(null)
    setWorldParams({ ...worldParams, imported: null })
    setIsWorldEmpty(true)
  }

  function createNewEditorGames(params: WorldParams): Games {
    const games = new Games(false)
    const agents = new Agents(games)
    const world = World.fromParams(params.width, params.height, params.initialEnergy)
    const game = new Game(games, world, agents)
    games.currentGame = game
    return games
  }

  const handleImport = async (
    e: React.ChangeEvent<HTMLInputElement>
  ): Promise<void> => {
    const file = e.target.files?.[0]
    if (!file) {
      return
    }
    importWorld(file).then((games) => {
      const world = games.currentGame!.currentRound.world
      setWorldParams({
        width: world.size.width,
        height: world.size.height,
        initialEnergy: world.startEnergy,
        imported: games,
      })
    })
    // Reset so we can import the same file after we clear (weird edge case ngl)
    e.target.value = ""
  }

  const handleParamChange = (name: string, val: number): void => {
    setEditorGames(null)
    setWorldParams((prev) => ({ ...prev, [name]: val, imported: null }))
  }

  const handleBrushChange = (name: string): void => {
    setBrushes((prev) => prev.map((b) => b.withOpen(b.name === name)))
  }

  const applyBrush = (loc: { x: number; y: number }, rightClick: boolean): void => {
    if (!currentBrush) {
      return
    }

    const numberInputs = document.querySelectorAll('input[type="number"]')
    numberInputs.forEach((input) => {
      if (input instanceof HTMLInputElement) {
        input.blur()
      }
    })

    currentBrush.apply(loc.x, loc.y, currentBrush.fields, rightClick)
    Renderer.doFullRedraw()
    Renderer.fullRender()
    setIsWorldEmpty(worldEmpty())

    notify(ListenerKey.Round)
  }

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent): void => {
      if (e.key.toLowerCase() === "e" && hoveredTile) {
        e.preventDefault()
        setSelectedTile(hoveredTile)
        setIsEditorOpen(true)
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [hoveredTile])

  const handleClose = (): void => {
    setIsEditorOpen(false)
    setSelectedTile(undefined)
    Renderer.doFullRedraw()
    Renderer.fullRender()
  }

  const renderBrushes = useMemo(() => {
    return brushes.map((brush) => (
      <TabsContent key={brush.name} value={brush.name} className="mt-4 px-1">
        <Brush brush={brush} scaffold={scaffold} />
        {brush.name === "Layers" && (
          <div className="mt-2 p-3 rounded-lg bg-muted/30 border-dashed border">
            <p className="text-xs text-muted-foreground text-center">
              <kbd className="px-2 py-1 text-xs font-mono bg-muted rounded border">
                e
              </kbd>{" "}
              to edit cell layers when hovering a cell.
            </p>
          </div>
        )}
      </TabsContent>
    ))
  }, [brushes])

  useEffect(() => {
    if (mouseDown && hoveredTile) {
      applyBrush(hoveredTile, rightClick)
    }
  }, [hoveredTile, rightClick, mouseDown])

  if (!isOpen || brushes.length === 0 || !currentBrush) {
    return null
  }

  return (
    <div className="flex flex-col gap-6 p-1">
      <div className="space-y-3">
        <h2 className="font-semibold tracking-tight">Brush Tools</h2>

        <Tabs
          value={currentBrush.name}
          onValueChange={handleBrushChange}
          className="w-full"
        >
          <TabsList className="grid w-full grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-1 h-auto p-1 bg-muted/50">
            {brushes.map((brush) => (
              <TabsTrigger
                key={brush.name}
                value={brush.name}
                className="text-xs font-medium py-2 px-3 data-[state=active]:bg-background data-[state=active]:shadow-sm transition-all duration-200"
              >
                {brush.name}
              </TabsTrigger>
            ))}
          </TabsList>
          {renderBrushes}
        </Tabs>
      </div>

      <Separator />

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold tracking-tight">World Configuration</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Configure map dimensions and initial settings
            </p>
          </div>
          <ConfirmClearDialog onConfirm={clearWorld} disabled={isWorldEmpty} />
        </div>

        <div
          className={cn(
            "grid grid-cols-1 sm:grid-cols-2 gap-4",
            !isWorldEmpty && "opacity-50 pointer-events-none bg-muted/10"
          )}
        >
          <div className="space-y-2">
            <Label htmlFor="width" className="text-xs text-muted-foreground">
              Width
            </Label>
            <NumberInput
              name="width"
              value={worldParams.width}
              min={MAP_MIN}
              max={MAP_MAX}
              onChange={handleParamChange}
            />
            <p className="text-xs text-muted-foreground">
              Range: {MAP_MIN}-{MAP_MAX}
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="height" className="text-xs text-muted-foreground">
              Height
            </Label>
            <NumberInput
              name="height"
              value={worldParams.height}
              min={MAP_MIN}
              max={MAP_MAX}
              onChange={handleParamChange}
            />
            <p className="text-xs text-muted-foreground">
              Range: {MAP_MIN}-{MAP_MAX}
            </p>
          </div>

          <div className="col-span-1 sm:col-span-2 space-y-2">
            <Label htmlFor="initialEnergy" className="text-xs text-muted-foreground">
              Initial Energy
            </Label>
            <NumberInput
              name="initialEnergy"
              value={worldParams.initialEnergy}
              min={1}
              max={1000}
              onChange={handleParamChange}
            />
            <p className="text-xs text-muted-foreground">Range: 1-1000</p>
          </div>
        </div>

        {!isWorldEmpty && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-muted border border-border">
            <div className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
            <p className="text-xs text-foreground">
              Clear the world to modify configuration settings
            </p>
          </div>
        )}
      </div>

      <Separator />

      <div className="space-y-4">
        <div>
          <h2 className="font-semibold tracking-tight">Import & Export</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Export your world or import existing world files
          </p>
        </div>

        <div className="flex flex-col xl:flex-row gap-3">
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            className="flex-1 items-center h-10"
          >
            <Upload />
            Import
          </Button>

          <ExportDialog
            onConfirm={async (filename) => {
              const error = await exportWorld(round!, filename)
              return error
            }}
          />
        </div>
      </div>

      <LayerEditor
        tile={isEditorOpen ? selectedTile : undefined}
        round={round}
        onClose={handleClose}
      />

      <input
        type="file"
        accept=".world"
        ref={fileInputRef}
        onChange={handleImport}
        hidden
      />
    </div>
  )
}
