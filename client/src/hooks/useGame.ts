import { useEffect, useState } from "react"
import { ListenerKey, subscribe } from "@/core/Listeners"
import Game from "@/core/Game"
import useGames from "./useGames"

export default function useGame(): Game | undefined {
  const games = useGames()
  const [, setGame] = useState(games?.currentGame)
  const [, setMaxRound] = useState(games?.currentGame?.maxRound)

  useEffect(() => {
    const unsubscribe = subscribe(ListenerKey.Game, () => {
      setGame(games?.currentGame)
      setMaxRound(games?.currentGame?.maxRound)
    })
    return unsubscribe
  }, [games])

  return games?.currentGame
}
