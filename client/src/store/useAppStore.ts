import Games from "@/core/Games"
import { create } from "zustand"

interface AppState {
  queue: Games[]
  editorGames: Games | null
  collapsedPanels: Record<string, boolean>
  selectedAgentId: number | null

  setQueue: (queue: Games[]) => void
  pushToQueue: (game: Games) => void
  clearQueue: () => void

  setEditorGames: (games: Games | null) => void
  togglePanel: (panelId: string) => void
  setSelectedAgentId: (agentId: number | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  queue: [],
  editorGames: null,
  collapsedPanels: {},
  selectedAgentId: null,

  setQueue: (queue): void => set({ queue }),
  pushToQueue: (game): void => set((state) => ({ queue: [...state.queue, game] })),
  clearQueue: (): void => set({ queue: [] }),

  setEditorGames: (games): void => set({ editorGames: games }),
  togglePanel: (panelId: string): void =>
    set((state) => ({
      ...state,
      collapsedPanels: {
        ...state.collapsedPanels,
        [panelId]: !state.collapsedPanels[panelId],
      },
    })),
  setSelectedAgentId: (agentId: number | null): void =>
    set({ selectedAgentId: agentId }),
}))
