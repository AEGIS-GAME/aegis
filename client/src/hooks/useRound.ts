import { ListenerKey, subscribe } from "@/core/Listeners"
import type Round from "@/core/Round"
import { useCallback, useEffect, useState } from "react"
import useGame from "./useGame"

export default function useRound(): Round | undefined {
  const game = useGame()
  const [round, setRound] = useState(game?.currentRound)

  useEffect(() => {
    const unsubscribe = subscribe(ListenerKey.Round, () => {
      setRound(game?.currentRound)
    })

    return unsubscribe
  }, [game])

  useEffect(() => {
    setRound(game?.currentRound)
  }, [game])

  return round
}

export function useRoundWithVersion(): { round: Round | undefined; version: number } {
  const game = useGame()
  const [round, setRound] = useState(game?.currentRound)
  const [roundVersion, setRoundVersion] = useState(0)

  const forceUpdate = useCallback(() => {
    setRoundVersion((prev) => prev + 1)
  }, [])

  useEffect(() => {
    const unsubscribe = subscribe(ListenerKey.Round, () => {
      forceUpdate()
      setRound(game?.currentRound)
    })

    return unsubscribe
  }, [game, forceUpdate])

  useEffect(() => {
    setRound(game?.currentRound)
    setRoundVersion(0)
  }, [game])

  return { round, version: roundVersion }
}
