import { schema } from "aegis-schema"
import Agents from "./Agents"
import Games from "./Games"
import { ListenerKey, notify } from "./Listeners"
import Round from "./Round"
import RoundStats from "./Stats"
import World from "./World"

const SNAPSHOT_INTERVAL = 25

export default class Game {
  public maxRound: number = 1
  public currentRound: Round
  public readonly stats: RoundStats[] = []
  private readonly rounds: schema.Round[] = []
  private readonly snapshots: Round[] = []

  /**
   * Initializes the Game with the given world map.
   * @param {Games} games - The games wrapper.
   * @param {World} world - The initial world map for the simulation.
   * @param {Agents} initialAgents - The initial agents that will spawn.
   */
  constructor(
    public readonly games: Games,
    public readonly world: World,
    public initialAgents: Agents
  ) {
    this.currentRound = new Round(this, this.world.copy(), 0, initialAgents)
  }

  public static fromSchema(games: Games, header: schema.GameHeader): Game {
    const world = World.fromSchema(header.world!)
    const initialAgents = new Agents(games, header.spawns)
    return new Game(games, world, initialAgents)
  }

  public addRound(round: schema.Round): void {
    if (this.currentRound.round === 0) {
      this.currentRound.startRound(round)
      this.snapshots.push(this.currentRound.copy())
    }
    this.rounds.push(round)
    this.maxRound++

    // idk why maxRound isn't updating properly,
    // so im adding this here for now
    notify(ListenerKey.Game)
  }

  public stepRound(step: number): void {
    this.jumpToRound(this.currentRound.round + step)
  }

  /**
   * Jumps to a specified round and updates the simulation state.
   * @param {number} round - The round to jump to.
   */
  public jumpToRound(round: number): void {
    if (this.snapshots.length === 0) {
      return
    }

    const clampedRound = Math.max(1, Math.min(round, this.maxRound))
    if (clampedRound === this.currentRound.round) {
      return
    }

    const snapshot = this.getClosestSnapshot(clampedRound)

    const updatingRound =
      this.currentRound.round >= snapshot.round &&
      this.currentRound.round <= clampedRound
        ? this.currentRound
        : snapshot.copy()

    if (updatingRound.round === 1 && clampedRound === 1) {
      // reset this game back to the original state from the GameHeader
      this.currentRound = new Round(this, this.world, 0, this.initialAgents)
    }

    console.log(
      "updatingRound",
      updatingRound,
      "clampedRound",
      clampedRound,
      "currentRound",
      this.currentRound
    )
    while (updatingRound.round < clampedRound) {
      updatingRound.jumpToTurn(updatingRound.turnsLength)
      const nextDelta =
        updatingRound.round < this.rounds.length
          ? this.rounds[updatingRound.round]
          : null

      updatingRound.startRound(nextDelta)
      if (updatingRound.round % SNAPSHOT_INTERVAL === 0) {
        this.snapshots.push(updatingRound.copy())
      }
    }

    this.currentRound = updatingRound
    notify(ListenerKey.Round)
  }

  public stepGame(): [boolean, boolean] {
    const round = this.currentRound.round
    const turn = this.currentRound.turn

    this.currentRound.jumpToTurn(this.currentRound.turnsLength)
    this.stepRound(1)

    const roundChanged = round !== this.currentRound.round
    const turnChanged = turn !== this.currentRound.turn || roundChanged
    return [roundChanged, turnChanged]
  }

  // public stepTurn(turns: number): void {
  //   let targetTurn = this.currentRound.turn + turns
  // }

  private getClosestSnapshot(targetRound: number): Round {
    const snapIndex = Math.floor((targetRound - 1) / SNAPSHOT_INTERVAL)
    if (snapIndex < this.snapshots.length) {
      return this.snapshots[snapIndex]
    }
    return this.snapshots[this.snapshots.length - 1]
  }

  public initEnergy(): void {
    for (const agent of this.initialAgents.agents.values()) {
      agent.energyLevel = this.world.startEnergy
    }
  }
}
