import { ROUND_INTERVAL_DURATION } from "@/utils/constants"
import Game from "./Game"
import Games from "./Games"
import { ListenerKey, notify } from "./Listeners"
import { Renderer } from "./Renderer"

class RunnerClass {
  private gameLoop: NodeJS.Timeout | undefined = undefined
  games: Games | undefined = undefined
  paused: boolean = true

  get game(): Game | undefined {
    return this.games?.currentGame
  }

  private startGameLoop(): void {
    if (this.gameLoop) {
      return
    }

    this.gameLoop = setInterval(() => {
      if (!this.game || this.paused) {
        this.stopGameLoop()
        return
      }
      const [roundChanged] = this.game.stepGame()
      Renderer.render()
      if (roundChanged) {
        notify(ListenerKey.Round)
      }
      if (this.game.currentRound.isEnd()) {
        this.setPaused(true)
      }
    }, ROUND_INTERVAL_DURATION)
  }

  private stopGameLoop(): void {
    if (!this.gameLoop) {
      return
    }
    clearInterval(this.gameLoop)
    this.gameLoop = undefined
  }

  private updateGameLoop(): void {
    if (!this.game || this.paused) {
      this.stopGameLoop()
      return
    }
    this.startGameLoop()
  }

  public setPaused(paused: boolean): void {
    if (!this.game) {
      return
    }
    this.paused = paused
    this.updateGameLoop()
    notify(ListenerKey.Control)
  }

  public setGames(games: Games | undefined): void {
    if (this.games === games) {
      return
    }
    this.games = games
    notify(ListenerKey.Games)
  }

  public setGame(game: Game | undefined): void {
    if (game) {
      game.games.currentGame = game
      this.setGames(game.games)
      game.jumpToRound(1)
      Renderer.render()
    }
    this.setPaused(true)
    Renderer.onGameChange()
    notify(ListenerKey.Game)
  }

  public stepRound(step: number): void {
    if (!this.game) {
      return
    }
    this.game.stepRound(step)
    Renderer.doFullRedraw()
    Renderer.render()
    notify(ListenerKey.Round)
  }

  public jumpToRound(round: number): void {
    if (!this.game || this.game.currentRound.round === round) {
      return
    }
    this.game.jumpToRound(round)
    Renderer.doFullRedraw()
    Renderer.render()
    notify(ListenerKey.Round)
  }

  public nextMatch(): void {
    if (!this.game || !this.games) {
      return
    }
    const prevIndex = this.games.games.indexOf(this.game)
    if (prevIndex + 1 === this.games.games.length) {
      this.setGames(undefined)
    } else {
      this.setGame(this.games.games[prevIndex + 1])
    }
  }

  public prevMatch(): void {
    if (!this.game || !this.games) {
      return
    }
    const prevIndex = this.games.games.indexOf(this.game)
    if (prevIndex > 0) {
      this.setGame(this.games.games[prevIndex - 1])
    }
  }
}

export const Runner = new RunnerClass()
