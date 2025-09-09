import { Progress } from "@/components/ui/progress"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Runner } from "@/core/Runner"
import { useRoundWithVersion } from "@/hooks/useRound"
import { TIMELINE_WIDTH } from "@/utils/constants"
import { MouseEvent } from "react"
import invariant from "tiny-invariant"

export default function Timeline(): JSX.Element {
  const { round } = useRoundWithVersion()

  // Convert internal round number to display round number (completed rounds)
  const getDisplayRound = (internalRound: number): number =>
    Math.max(0, internalRound - 1)

  // Convert display round number to internal round number
  const getInternalRound = (displayRound: number): number => displayRound + 1

  const handleSeek = (e: MouseEvent<HTMLDivElement>): void => {
    invariant(round, "Somehow using an undefined round to seek")

    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const progress = Math.max(0, Math.min(1, x / TIMELINE_WIDTH))
    const targetDisplayRound = Math.floor(progress * (round.game.maxRound - 1))
    Runner.jumpToRound(getInternalRound(targetDisplayRound))
  }

  if (!round) {
    return (
      <div
        className="text-xs text-muted-foreground flex items-center justify-center"
        style={{ minWidth: TIMELINE_WIDTH }}
      >
        Waiting for simulation...
      </div>
    )
  }

  const maxRound = round.game.maxRound
  const progressPercentage =
    maxRound > 0 ? (getDisplayRound(round.round) / Math.max(1, maxRound - 1)) * 100 : 0

  return (
    <TooltipProvider>
      <div className="w-full mx-auto space-y-1">
        <div className="flex justify-center items-center mb-1">
          <span className="text-xs text-gray-600">Round:</span>
          <span className="text-xs ml-1">
            <b>{getDisplayRound(round.round)}</b> / {Math.max(0, maxRound - 1)}
          </span>
        </div>
        <Tooltip>
          <TooltipTrigger asChild>
            <div
              className="relative cursor-pointer"
              onClick={handleSeek}
              style={{ minWidth: TIMELINE_WIDTH }}
            >
              <Progress value={progressPercentage} className="w-full h-2" />
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <p>Click to jump to a specific round</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  )
}
