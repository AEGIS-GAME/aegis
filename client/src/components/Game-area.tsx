import { Renderer } from "@/core/Renderer"
import useHover from "@/hooks/useHover"
import { useRoundWithVersion } from "@/hooks/useRound"
import { useEffect, useMemo, useRef } from "react"

export default function GameArea(): JSX.Element {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const hoveredTile = useHover()
  const { round, version } = useRoundWithVersion()

  useEffect(() => {
    if (round && containerRef.current) {
      Renderer.renderToContainer(containerRef.current)
    }
  }, [round])

  const hoveredCell = useMemo(() => {
    return hoveredTile && round
      ? round.world.cellAt(hoveredTile.x, hoveredTile.y)
      : undefined
  }, [hoveredTile, round, version])

  return (
    <div className="relative flex justify-center items-center w-full h-screen">
      {round ? (
        <>
          <div ref={containerRef} className="absolute inset-0" />
          {hoveredTile && (
            <div className="absolute top-1 left-1 z-50 bg-black/70 text-white p-2 rounded-lg pointer-events-none text-sm font-semibold">
              <div>{`(X: ${hoveredTile.x}, Y: ${hoveredTile.y})`}</div>
              {hoveredCell && (
                <div className="text-sm font-semibold mt-1">
                  Move Cost: {hoveredCell.moveCost}
                </div>
              )}
            </div>
          )}
        </>
      ) : (
        <div className="text-muted-foreground">Waiting for game to start...</div>
      )}
    </div>
  )
}
