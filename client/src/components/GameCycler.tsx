import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Runner } from "@/core/Runner"

export default function GameCycler(): JSX.Element | null {
  const [index, setIndex] = useState<number>(-1)
  const [total, setTotal] = useState<number>(0)

  useEffect(() => {
    const games = Runner.games?.games || []
    const current = Runner.game
    setTotal(games.length)
    setIndex(current ? games.indexOf(current) : -1)
  }, [Runner.game, Runner.games])

  const goPrev = (): void => {
    Runner.prevMatch()
    setIndex((i) => Math.max(i - 1, -1))
  }

  const goNext = (): void => {
    Runner.nextMatch()
    setIndex((i) => (i + 1 >= total ? -1 : i + 1))
  }

  if (!Runner.games || total === 0 || total === 1) {
    return null
  }

  return (
    <div className="flex items-center justify-center space-x-2">
      <Button onClick={goPrev} disabled={index <= 0} size="icon">
        <ChevronLeft />
      </Button>

      <span className="text-sm text-muted-foreground">
        {index >= 0 ? `Match ${index + 1} of ${total}` : "No match selected"}
      </span>

      <Button onClick={goNext} disabled={index + 1 >= total} size="icon">
        <ChevronRight />
      </Button>
    </div>
  )
}
