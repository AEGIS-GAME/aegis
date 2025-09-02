import { ListenerKey, subscribe } from "@/core/Listeners"
import { Renderer } from "@/core/Renderer"
import type { Vector } from "@/types"
import { useEffect, useState } from "react"

export default function useHover(): Vector | undefined {
  const [hovered, setHovered] = useState(Renderer.getHoveredTile())

  useEffect(() => {
    const unsubscribe = subscribe(ListenerKey.Hover, () => {
      setHovered(Renderer.getHoveredTile())
    })

    return unsubscribe
  }, [])

  return hovered
}
