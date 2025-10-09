import { Button } from "@/components/ui/button"
import { SidebarView } from "@/types"
import {
  ChartBarBig,
  ChevronLeft,
  Gamepad2,
  Pencil,
  Settings as SettingsIcon,
} from "lucide-react"
import { useEffect, useState, useRef, useCallback } from "react"

import { ListenerKey, subscribe } from "@/core/Listeners"
import { Renderer } from "@/core/Renderer"
import useGames from "@/hooks/useGames"
import { createScaffold } from "@/services"
import Console from "../Console"
import Editor from "../editor/Editor"
import { ErrorMessage } from "../ui/error-message"
import Aegis from "./Aegis"
import Game from "./Game"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip"
import SettingsModal from "./SettingsModal"

const sidebarItems = [
  { id: SidebarView.Aegis, icon: Gamepad2, label: "Start Game" },
  { id: SidebarView.Game, icon: ChartBarBig, label: "Game Stats" },
  { id: SidebarView.Editor, icon: Pencil, label: "Game Editor" },
  { id: SidebarView.Settings, icon: SettingsIcon, label: "Settings" },
]

export default function Sidebar(): JSX.Element {
  const scaffold = createScaffold()
  const { aegisPath, setupAegisPath, output, spawnError } = scaffold
  const games = useGames()
  const [selectedView, setSelectedView] = useState<SidebarView | null>(
    SidebarView.Aegis
  )
  const [settingsModalOpen, setSettingsModalOpen] = useState(false)
  const [width, setWidth] = useState(320)
  const [isDragging, setIsDragging] = useState(false)
  const dragRef = useRef({ startX: 0, startWidth: 0 })

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault()
      setIsDragging(true)
      document.body.style.userSelect = "none"
      dragRef.current = { startX: e.clientX, startWidth: width }
    },
    [width]
  )

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging) {
        return
      }
      const { startX, startWidth } = dragRef.current
      const newWidth = Math.max(192, Math.min(480, startWidth + e.clientX - startX))
      setWidth(newWidth)
    },
    [isDragging]
  )

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
    document.body.style.userSelect = ""
  }, [])

  useEffect(() => {
    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
    } else {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [isDragging, handleMouseMove, handleMouseUp])

  useEffect(() => {
    const unsubscribe = subscribe(ListenerKey.LayerViewer, () => {
      const tile = Renderer.getLayerViewerTile()
      if (tile && games?.playable) {
        setSelectedView(SidebarView.Game)
      }
    })
    return unsubscribe
  }, [games?.playable])

  const handleSidebarClick = (itemId: SidebarView): void => {
    if (itemId === SidebarView.Settings) {
      setSettingsModalOpen(true)
    } else {
      setSelectedView(selectedView === itemId ? null : itemId)
    }
  }

  return (
    <div className="relative flex h-screen">
      <div
        className={`absolute top-4 -right-8 z-50 bg-accent rounded-full p-1 flex items-center justify-between
          ${!selectedView ? "hidden" : ""}`}
      >
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSelectedView(null)}
          className="h-4 w-4"
        >
          <ChevronLeft />
        </Button>
      </div>

      <div className="flex flex-col items-center py-4 w-16 h-full border-l">
        <TooltipProvider>
          {sidebarItems.map((item) => (
            <Tooltip key={item.id}>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  onClick={() => handleSidebarClick(item.id)}
                  className={`
                  p-3 my-2 rounded-xl transition-colors 
                  ${
                    selectedView === item.id
                      ? "text-foreground bg-accent"
                      : "text-muted-foreground hover:bg-accent"
                  }
                `}
                >
                  <item.icon />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{item.label}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </TooltipProvider>
      </div>

      <div
        className={`h-full overflow-hidden bg-background border-r relative ${
          isDragging ? "" : "transition-all duration-300"
        }`}
        style={{ width: selectedView ? `${width}px` : "0rem" }}
      >
        {selectedView && (
          <div className="flex flex-col h-full overflow-auto p-3 scrollbar">
            {!aegisPath ? (
              <Button onClick={setupAegisPath} className="w-full">
                Setup Aegis Path
              </Button>
            ) : (
              <>
                {selectedView === SidebarView.Aegis && <Aegis scaffold={scaffold} />}
                {selectedView === SidebarView.Game && <Game scaffold={scaffold} />}
                {/* Editor always has to be visible or else it wont remove the game if we switch tabs */}
                <Editor
                  isOpen={selectedView === SidebarView.Editor}
                  scaffold={scaffold}
                />
                {selectedView !== SidebarView.Settings &&
                  selectedView !== SidebarView.Editor && <Console output={output} />}
                {spawnError && (
                  <div className="mt-4">
                    <ErrorMessage title="Error" message={spawnError} />
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {selectedView && (
        <div
          className="absolute top-0 right-0 w-1 h-full cursor-col-resize select-none"
          onMouseDown={handleMouseDown}
        />
      )}

      <SettingsModal
        isOpen={settingsModalOpen}
        scaffold={scaffold}
        onClose={() => setSettingsModalOpen(false)}
      />
    </div>
  )
}
