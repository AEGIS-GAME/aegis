import { schema } from "aegis-schema"
import invariant from "tiny-invariant"
import Agents from "./Agents"
import Game from "./Game"
import RoundStats from "./Stats"
import World from "./World"

export default class Round {
  public turn: number = 0

  constructor(
    public readonly game: Game,
    public world: World,
    public round: number,
    public agents: Agents,
    private currentRound: schema.Round | null = null
  ) {
    if (round === 0) {
      this.stats.applyRound(this, null)
    }
  }

  public startRound(round: schema.Round | null): void {
    invariant(
      this.turn === this.turnsLength,
      "Cannot start new round without completing the previous one"
    )
    this.agents.processRound(this.currentRound)

    this.round += 1

    this.world.applyRound(this.currentRound)
    this.stats.applyRound(this, this.currentRound)

    this.turn = 0
    this.currentRound = round
  }

  public jumpToTurn(turn: number): void {
    if (!this.currentRound) {
      return
    }

    while (this.turn < turn) {
      this.stepTurn()
    }
  }

  private stepTurn(): void {
    const turn = this.currentRound!.turns[this.turn]
    invariant(turn, "Turn not found to step to")

    if (this.turn === 0) {
      this.agents.clearDead()
    }
    this.agents.applyTurn(turn)
    this.turn += 1
  }

  get turnsLength(): number {
    return this.currentRound?.turns.length ?? 0
  }

  get layersRemoved(): schema.Location[] {
    return this.currentRound?.layersRemoved ?? []
  }

  get droneScans(): schema.DroneScan[] {
    return this.currentRound?.droneScans ?? []
  }

  get stats(): RoundStats {
    const stats = this.game.stats[this.round]
    if (stats) {
      return stats
    }

    const newStats = new RoundStats(this.game)
    this.game.stats[this.round] = newStats
    return newStats
  }

  public copy(): Round {
    return new Round(
      this.game,
      this.world.copy(),
      this.round,
      this.agents.copy(),
      this.currentRound
    )
  }

  public isEnd(): boolean {
    return this.round === this.game.maxRound
  }
}
