import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Runner } from "@/core/Runner"
import useGame from "@/hooks/useGame"
import { cn } from "@/lib/utils"
import { ConsoleLine } from "@/types"
import RingBuffer from "@/utils/ringBuffer"
import { Maximize2 } from "lucide-react"
import { useState } from "react"

interface Props {
  output: RingBuffer<ConsoleLine>
}

export default function Console({ output }: Props): JSX.Element {
  const [isPopupOpen, setIsPopupOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const game = useGame()

  const highlightMatch = (text: string, query: string): JSX.Element => {
    if (!query) {
      return <>{text}</>
    }

    const parts = text.split(new RegExp(`(${query})`, "gi"))
    return (
      <>
        {parts.map((part, i) => (
          <span
            key={i}
            className={
              part.toLowerCase() === query.toLowerCase() ? "bg-yellow-200" : ""
            }
          >
            {part}
          </span>
        ))}
      </>
    )
  }

  const renderOutput = (): JSX.Element => {
    return (
      <div className="p-2 h-full border-2 border-accent-light rounded-md text-xs overflow-auto whitespace-nowrap scrollbar">
        {output
          .getItems()
          .filter((line) => {
            // If there's no current game, show messages with gameIdx 0 (startup errors)
            if (!game || !Runner.games) {
              return line.gameIdx === 0
            }
            return line.gameIdx === Runner.games.games.indexOf(game)
          })
          .map((line, i) => {
            const matches =
              searchTerm &&
              line.content.toLowerCase().includes(searchTerm.toLowerCase())

            if (
              line.content.toLowerCase().includes("tensorflow") &&
              (line.content.toLowerCase().includes("warning") ||
                line.content.toLowerCase().includes("onednn"))
            ) {
              line.has_error = false
            }

            return (
              <div
                key={i}
                className={cn(
                  "whitespace-pre break-words pt-1",
                  line.has_error && "text-destructive",
                  matches && "bg-muted"
                )}
              >
                {highlightMatch(line.content, searchTerm)}
              </div>
            )
          })}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mt-auto w-full h-[300px] flex flex-col">
        <div className="flex justify-between items-center">
          <h2 className="font-bold">Console</h2>
          <Button variant="ghost" size="icon" onClick={() => setIsPopupOpen(true)}>
            <Maximize2 />
          </Button>
        </div>
        <div className="flex-1 min-h-0">{renderOutput()}</div>
      </div>
      <Dialog open={isPopupOpen} onOpenChange={setIsPopupOpen}>
        <DialogContent
          className="min-w-[90vw] h-[90vh] flex flex-col"
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              setSearchTerm("")
            }
          }}
        >
          <DialogHeader>
            <DialogTitle>Console</DialogTitle>
            <DialogDescription>Press ESC to close</DialogDescription>
          </DialogHeader>
          <div className="mb-2">
            <Input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          {renderOutput()}
        </DialogContent>
      </Dialog>
    </div>
  )
}
