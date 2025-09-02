import { schema } from "aegis-schema"
import Game from "./Game"
import Round from "./Round"
import invariant from "tiny-invariant"

export default class RoundStats {
  private readonly _teams: Map<schema.Team, TeamStats>
  private readonly game: Game

  constructor(game: Game, teams?: Map<schema.Team, TeamStats>) {
    this.game = game
    this._teams =
      teams ??
      new Map([
        [schema.Team.GOOBS, new TeamStats()],
        [schema.Team.VOIDSEERS, new TeamStats()],
      ])
  }

  public getTeamStats(team: schema.Team): TeamStats {
    const stats = this._teams.get(team)
    invariant(stats, "team not found in `getTeamStats`")
    return stats
  }

  public get teams(): Map<schema.Team, TeamStats> {
    return this._teams
  }

  applyRound(round: Round, delta: schema.Round | null): void {
    if (delta) {
      for (let i = 0; i < delta.teamInfo.length; i++) {
        const teamInfo = delta.teamInfo[i]
        const teamStats = this._teams.get(teamInfo.team)

        invariant(teamStats, "team not found in `applyRound` for stats")

        teamStats.saved_alive = teamInfo.savedAlive
        teamStats.saved_dead = teamInfo.savedDead
        teamStats.saved = teamInfo.saved
        teamStats.predicted_right = teamInfo.predictedRight
        teamStats.predicted_wrong = teamInfo.predictedWrong
        teamStats.predicted = teamInfo.predicted
        teamStats.score = teamInfo.score
      }
    }

    for (const stat of this._teams.values()) {
      stat.units = 0
    }

    for (const agent of round.agents.agents.values()) {
      const teamStats = round.stats.getTeamStats(agent.team)
      teamStats.units++
    }
  }
}

class TeamStats {
  saved_alive: number = 0
  saved_dead: number = 0
  saved: number = 0
  predicted_right: number = 0
  predicted_wrong: number = 0
  predicted: number = 0
  score: number = 0
  units: number = 0
}
