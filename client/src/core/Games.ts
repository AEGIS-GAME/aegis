import { schema } from "aegis-schema"
import Game from "./Game"
import invariant from "tiny-invariant"

let nextId = 0

export default class Games {
  public readonly games: Game[] = []
  public currentGame: Game | undefined = undefined
  public readonly id: number
  public playable: boolean

  constructor(playable: boolean) {
    this.id = nextId++
    this.playable = playable
  }

  /**
   * Adds a new event.
   * @param {Event} event - The event wrapper.
   */
  addEvent(event: schema.Event): void {
    switch (event.event.oneofKind) {
      case "gamesHeader":
        invariant(false, "Cannot add another GamesHeader event.")
      // fallthrough intentional because invariant throws
      // eslint-disable-next-line no-fallthrough
      case "gameHeader": {
        const header = event.event.gameHeader
        const game = Game.fromSchema(this, header)
        this.games.push(game)
        this.currentGame = game
        game.initEnergy()
        return
      }
      case "round": {
        invariant(this.currentGame, "Cannot add rounds to an undefined game.")
        const round = event.event.round
        this.currentGame.addRound(round)
        return
      }
      case "gameFooter":
        return
      case "gamesFooter":
        return
    }
  }
}
