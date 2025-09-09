import { useEffect, useState } from "react"
import { ListenerKey, subscribe } from "@/core/Listeners"
import { Runner } from "@/core/Runner"

export default function useControl(): boolean {
  const [paused, setPaused] = useState(Runner.paused)

  useEffect(() => {
    const unsubscribe = subscribe(ListenerKey.Control, () => {
      setPaused(Runner.paused)
    })

    return unsubscribe
  }, [])

  return paused
}
