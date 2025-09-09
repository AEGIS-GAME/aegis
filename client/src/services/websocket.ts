import Game from "@/core/Game"
import Games from "@/core/Games"
import { schema } from "aegis-schema"
import invariant from "tiny-invariant"

export class ClientWebSocket {
  private url: string = "ws://localhost:6003"
  private reconnectInterval: number = 500
  private games: Games | undefined = undefined
  private game: Game | undefined = undefined

  constructor(
    readonly onGameCreated: (game: Game) => void,
    readonly onGamesCreated: (games: Games) => void
  ) {
    this.connect()
  }

  private connect(): void {
    const ws: WebSocket = new WebSocket(this.url)

    ws.onopen = (): void => {
      console.log(`Connected to ${this.url}`)
    }

    ws.onmessage = (event): void => {
      this.handleEvent(event.data)
    }

    ws.onclose = (): void => {
      this.game = undefined
      this.games = undefined
      setTimeout(() => this.connect(), this.reconnectInterval)
    }
  }

  private handleEvent(data: string): void {
    try {
      const decoded = Uint8Array.from(atob(data), (c) => c.charCodeAt(0))
      const event = schema.Event.fromBinary(decoded)

      if (!this.games) {
        invariant(
          event.event.oneofKind === "gamesHeader",
          "First event must be the GamesHeader."
        )

        this.games = new Games(true)
        this.onGamesCreated(this.games)
        return
      }

      this.games.addEvent(event)

      if (event.event.oneofKind === "round") {
        const games = this.games.games
        const game = games[games.length - 1]
        if (this.game === game) {
          return
        }

        this.onGameCreated(game)
        this.game = game
      }

      if (event.event.oneofKind === "droneScanUpdate") {
        if (this.game) {
          this.game.currentRound.world.applyDroneScanUpdate(event.event.droneScanUpdate)
        }
      }

      if (event.event.oneofKind === "gameFooter") {
        this.game = undefined
      }
    } catch (error) {
      console.error("Failed to handle websocket event:", error)
    }
  }
}
