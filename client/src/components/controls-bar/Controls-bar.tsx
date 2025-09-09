import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { AnimatePresence, motion } from "framer-motion"
import { Maximize2, Minimize2, Pause, Play, SkipBack, SkipForward } from "lucide-react"
import { useState } from "react"
import Timeline from "./Timeline"
import useRound from "@/hooks/useRound"
import useControl from "@/hooks/useControl"
import { Runner } from "@/core/Runner"

function ControlsBar(): JSX.Element | null {
  const paused = useControl()
  const round = useRound()
  const [isMinimized, setIsMinimized] = useState<boolean>(false)

  if (!round) {
    return null
  }

  return (
    <TooltipProvider>
      <AnimatePresence>
        {isMinimized ? (
          <motion.div
            key="minimized-button"
            initial={{ opacity: 0, scale: 0.5, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.5, y: 50 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 20,
            }}
            className="fixed bottom-2 left-2 z-50"
          >
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={(): void => setIsMinimized(false)}
                >
                  <Maximize2 className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Expand Controls</p>
              </TooltipContent>
            </Tooltip>
          </motion.div>
        ) : (
          <motion.div
            key="full-controls"
            initial={{ opacity: 0, scale: 0.5, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.5, y: 50 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 20,
            }}
            className="fixed bottom-2 z-50"
          >
            <div className="flex items-center bg-white/90 rounded-full shadow-lg border border-gray-200 p-1">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(): void => setIsMinimized(true)}
                  >
                    <Minimize2 className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Minimize Controls</p>
                </TooltipContent>
              </Tooltip>

              <div className="mx-2">
                <Timeline />
              </div>

              <div className="flex items-center pr-1">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(): void => Runner.stepRound(-1)}
                      disabled={!round}
                    >
                      <SkipBack className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Previous Round</p>
                  </TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(): void => Runner.setPaused(!paused)}
                      disabled={!round}
                    >
                      {paused ? (
                        <Play className="h-4 w-4" />
                      ) : (
                        <Pause className="h-4 w-4" />
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{Runner.paused ? "Play" : "Pause"}</p>
                  </TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(): void => Runner.stepRound(1)}
                      disabled={!round}
                    >
                      <SkipForward className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Next Round</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </TooltipProvider>
  )
}

export default ControlsBar
