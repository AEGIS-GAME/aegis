import { ListenerKey, subscribe } from "@/core/Listeners"
import { Renderer } from "@/core/Renderer"
import type { Vector } from "@/types"
import { useEffect, useState } from "react"

export default function useSelectedTile(): Vector | undefined {
  const [selectedTile, setSelectedTile] = useState(Renderer.getSelectedTile())

  useEffect(() => {
    const unsubscribe = subscribe(ListenerKey.Canvas, () => {
      setSelectedTile(Renderer.getSelectedTile())
    })

    return unsubscribe
  }, [])

  return selectedTile
}
