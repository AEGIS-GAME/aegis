export enum ListenerKey {
  Games = "games",
  Game = "game",
  Round = "round",
  Control = "control",
  Canvas = "canvas",
  Hover = "hover",
  LayerViewer = "layerViewer",
}

type Listener = () => void

const listenersMap: Record<ListenerKey, Listener[]> = {
  [ListenerKey.Games]: [],
  [ListenerKey.Game]: [],
  [ListenerKey.Round]: [],
  [ListenerKey.Control]: [],
  [ListenerKey.Canvas]: [],
  [ListenerKey.Hover]: [],
  [ListenerKey.LayerViewer]: [],
}

export function subscribe(key: ListenerKey, listener: Listener): () => void {
  if (!listenersMap[key]) {
    listenersMap[key] = []
  }
  listenersMap[key].push(listener)

  return () => {
    listenersMap[key] = listenersMap[key].filter((l) => l !== listener)
  }
}

export function notify(key: ListenerKey): void {
  listenersMap[key]?.forEach((listener) => listener())
}
