import goobA from "@/assets/goob-team-a.png"
import goobB from "@/assets/goob-team-b.png"
import { useRoundWithVersion } from "@/hooks/useRound"
import { useAppStore } from "@/store/useAppStore"
import { Scaffold } from "@/types"
import { schema } from "aegis-schema"
import { ChevronDown, ChevronUp, MapPin, User, Users, Zap } from "lucide-react"
import { AnimatedContainer } from "./ui/animated-container"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { Card, CardContent } from "./ui/card"
import { EmptyState } from "./ui/empty-state"

interface Props {
  scaffold: Scaffold
}

function getTeamLabel(team: schema.Team): string {
  switch (team) {
    case schema.Team.GOOBS:
      return "Goob"
    case schema.Team.VOIDSEERS:
      return "Voidseer"
    default:
      return "Unknown"
  }
}

function getTeamIcon(team: schema.Team): string {
  switch (team) {
    case schema.Team.GOOBS:
      return goobA
    case schema.Team.VOIDSEERS:
      return goobB
    default:
      return goobA
  }
}

function getTeamColor(team: schema.Team): string {
  switch (team) {
    case schema.Team.GOOBS:
      return "bg-blue-100 text-blue-800 border-blue-200"
    case schema.Team.VOIDSEERS:
      return "bg-purple-100 text-purple-800 border-purple-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

export default function AgentView({ scaffold }: Props): JSX.Element {
  const { collapsedPanels, togglePanel, selectedAgentId, setSelectedAgentId } =
    useAppStore()
  const isCollapsed = collapsedPanels["agentView"] ?? false
  const { round } = useRoundWithVersion()

  const agent =
    selectedAgentId && round ? round.agents.agents.get(selectedAgentId) : undefined

  const clearSelection = (): void => {
    setSelectedAgentId(null)
  }

  const renderAgentDetails = (): JSX.Element => {
    if (!agent || !round) {
      return (
        <EmptyState
          message="Click on an agent in the Cell View to see its details"
          className="py-8"
        />
      )
    }

    const isVersusMode = scaffold.config?.configType === "competition"
    const teamLabel = getTeamLabel(agent.team)
    const teamIcon = getTeamIcon(agent.team)
    const teamColor = getTeamColor(agent.team)

    return (
      <AnimatedContainer key={`agent-${agent.id}`} className="space-y-3">
        <Card>
          <CardContent className="p-4">
            <div className="space-y-4">
              {/* Agent Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <img src={teamIcon} alt={teamLabel} className="w-8 h-8" />
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={`${teamColor} font-medium`}>
                        <User className="w-3 h-3 mr-1" />
                        {teamLabel}
                      </Badge>
                      <span className="text-sm font-medium">Agent #{agent.id}</span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Status: {agent.dead ? "Dead" : "Alive"}
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearSelection}
                  className="text-xs text-muted-foreground hover:text-foreground"
                >
                  Clear
                </Button>
              </div>

              {/* Agent Stats */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-600" />
                    <span className="text-sm font-medium">Energy Level</span>
                  </div>
                  <Badge variant="outline" className="font-mono text-sm">
                    {agent.energyLevel}
                  </Badge>
                </div>
              </div>

              {/* Position Information */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium">Current Position</span>
                  </div>
                  <Badge variant="outline" className="font-mono text-sm">
                    ({agent.loc.x}, {agent.loc.y})
                  </Badge>
                </div>
                {(agent.loc.x !== agent.lastLoc.x ||
                  agent.loc.y !== agent.lastLoc.y) && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4" /> {/* Spacer to align with above */}
                      <span className="text-xs text-muted-foreground">
                        Previous Position
                      </span>
                    </div>
                    <Badge variant="secondary" className="font-mono text-xs">
                      ({agent.lastLoc.x}, {agent.lastLoc.y})
                    </Badge>
                  </div>
                )}
              </div>

              {/* Team Information (only show in versus mode) */}
              {isVersusMode && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-purple-600" />
                    <span className="text-sm font-medium">Team</span>
                  </div>
                  <Badge variant="outline" className={`${teamColor} font-medium`}>
                    {teamLabel}
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </AnimatedContainer>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-purple-600" />
          <h3 className="font-semibold text-sm">Agent View</h3>
          {selectedAgentId && (
            <Badge variant="secondary" className="text-xs">
              #{selectedAgentId}
            </Badge>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => togglePanel("agentView")}
          className="h-6 w-6 p-0"
        >
          {isCollapsed ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronUp className="w-4 h-4" />
          )}
        </Button>
      </div>

      {!isCollapsed && (
        <AnimatedContainer className="space-y-2">
          {renderAgentDetails()}
        </AnimatedContainer>
      )}
    </div>
  )
}
