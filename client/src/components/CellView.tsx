import goobA from "@/assets/goob-team-a.png"
import goobB from "@/assets/goob-team-b.png"
import type Round from "@/core/Round"
import { useRoundWithVersion } from "@/hooks/useRound"
import useSelectedTile from "@/hooks/useSelectedTile"
import { useAppStore } from "@/store/useAppStore"
import { Scaffold } from "@/types"
import { schema } from "aegis-schema"
import { ChevronDown, ChevronUp, Layers3, MapPin, User, Users } from "lucide-react"
import { useMemo } from "react"
import { getLayerColor, getLayerIcon } from "./dnd/dnd-utils"
import { AnimatedContainer } from "./ui/animated-container"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { Card, CardContent } from "./ui/card"
import { EmptyState } from "./ui/empty-state"

interface Props {
  scaffold: Scaffold
}

function getCellTypeLabel(cellType: schema.CellType): string {
  switch (cellType) {
    case schema.CellType.NORMAL:
      return "Normal"
    case schema.CellType.SPAWN:
      return "Spawn"
    case schema.CellType.KILLER:
      return "Killer"
    case schema.CellType.CHARGING:
      return "Charging"
    default:
      return "Unknown"
  }
}

function getCellTypeColor(cellType: schema.CellType): string {
  switch (cellType) {
    case schema.CellType.NORMAL:
      return "bg-gray-100 text-gray-800 border-gray-200"
    case schema.CellType.SPAWN:
      return "bg-blue-100 text-blue-800 border-blue-200"
    case schema.CellType.KILLER:
      return "bg-red-100 text-red-800 border-red-200"
    case schema.CellType.CHARGING:
      return "bg-yellow-100 text-yellow-800 border-yellow-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

function getAgentsByTeam(
  agentIds: number[],
  round: Round
): { [key: string]: number[] } {
  const teamAgents: { [key: string]: number[] } = {
    [schema.Team.GOOBS]: [],
    [schema.Team.VOIDSEERS]: [],
  }

  for (const agentId of agentIds) {
    const agent = round.agents.agents.get(agentId)
    if (agent && !agent.dead) {
      if (agent.team === schema.Team.GOOBS) {
        teamAgents[schema.Team.GOOBS].push(agentId)
      } else if (agent.team === schema.Team.VOIDSEERS) {
        teamAgents[schema.Team.VOIDSEERS].push(agentId)
      }
    }
  }

  return teamAgents
}

export default function CellView({ scaffold }: Props): JSX.Element {
  const { collapsedPanels, togglePanel, setSelectedAgentId } = useAppStore()
  const isCollapsed = collapsedPanels["cellView"] ?? false
  const { round, version } = useRoundWithVersion()
  const selectedTile = useSelectedTile()

  const cell =
    selectedTile && round
      ? round.world.cellAt(selectedTile.x, selectedTile.y)
      : undefined

  // Memoize agent IDs to prevent unnecessary recalculations
  const agentIds = useMemo(() => {
    if (!round || !selectedTile) {
      return []
    }
    const ids: number[] = []
    for (const agent of round.agents.agents.values()) {
      if (
        !agent.dead &&
        agent.loc.x === selectedTile.x &&
        agent.loc.y === selectedTile.y
      ) {
        ids.push(agent.id)
      }
    }
    return ids
  }, [round, selectedTile, version])

  const handleAgentClick = (agentId: number): void => {
    setSelectedAgentId(agentId)
  }

  const renderAgents = (): JSX.Element => {
    if (!round || !selectedTile || agentIds.length === 0) {
      return <EmptyState message="No agents on this tile" />
    }

    const teamAgents = getAgentsByTeam(agentIds, round)
    const isVersusMode = scaffold.config?.configType === "competition"

    const teamConfigs = [
      {
        team: schema.Team.GOOBS,
        agents: teamAgents[schema.Team.GOOBS],
        icon: goobA,
        badgeClass: "bg-blue-100 text-blue-800 border-blue-200",
        label: "Goob",
        delay: 0.05,
      },
    ]

    if (isVersusMode && teamAgents[schema.Team.VOIDSEERS].length > 0) {
      teamConfigs.push({
        team: schema.Team.VOIDSEERS,
        agents: teamAgents[schema.Team.VOIDSEERS],
        icon: goobB,
        badgeClass: "bg-purple-100 text-purple-800 border-purple-200",
        label: "Voidseer",
        delay: 0.1,
      })
    }

    return (
      <div className="space-y-2">
        {teamConfigs.map((teamConfig) => (
          <div key={teamConfig.team} className="space-y-2">
            {teamConfig.agents.map((agentId) => (
              <AnimatedContainer
                key={agentId}
                className="flex items-center gap-2 rounded text-sm p-2 cursor-pointer hover:bg-accent/50 transition-colors group"
                delay={teamConfig.delay}
                onClick={() => handleAgentClick(agentId)}
              >
                <img
                  src={teamConfig.icon}
                  alt={teamConfig.label}
                  className="w-6 h-6 transition-transform group-hover:scale-110"
                />
                <Badge
                  variant="outline"
                  className={`${teamConfig.badgeClass} font-medium pointer-events-none`}
                >
                  <User className="w-3 h-3 mr-1" />
                  {teamConfig.label}
                </Badge>
                <span className="text-xs text-muted-foreground">ID: {agentId}</span>
              </AnimatedContainer>
            ))}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-blue-600" />
          <h3 className="font-semibold text-sm">Cell View</h3>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => togglePanel("cellView")}
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
        <div className="space-y-2">
          {!cell || !round ? (
            <div className="text-sm text-muted-foreground text-center py-4">
              Click on a cell to view its information
            </div>
          ) : (
            <>
              {selectedTile && (
                <div className="text-xs text-muted-foreground">
                  Position: ({selectedTile.x}, {selectedTile.y})
                </div>
              )}

              <div className="flex items-center justify-start gap-3">
                <div className="flex items-center gap-1">
                  <span className="text-xs font-medium">Move Cost:</span>
                  <Badge variant="outline" className="font-mono">
                    {cell.moveCost}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium">Type:</span>
                  <Badge
                    variant="outline"
                    className={`${getCellTypeColor(cell.type)} font-mono`}
                  >
                    {getCellTypeLabel(cell.type)}
                  </Badge>
                </div>
              </div>

              <Card>
                <CardContent className="p-3">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Agents:</span>
                    </div>

                    {renderAgents()}

                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Layers3 className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Layers:</span>
                      </div>

                      {cell.layers.length === 0 ? (
                        <EmptyState message="No layers on this tile" />
                      ) : (
                        <div className="space-y-0">
                          {cell.layers.map((layer, index) => (
                            <AnimatedContainer
                              key={index}
                              className="flex items-center gap-2 p-1 rounded text-sm"
                              delay={0.05 * (index + 1)}
                            >
                              <Badge
                                variant="outline"
                                className={`${getLayerColor(layer.object.oneofKind!)} font-medium`}
                              >
                                {getLayerIcon(layer.object.oneofKind!)}
                                <span className="ml-1 capitalize">
                                  {layer.object.oneofKind}
                                </span>
                              </Badge>

                              {layer.object.oneofKind === "survivor" && (
                                <>
                                  <span className="text-xs text-muted-foreground">
                                    ID: {layer.object.survivor.id}
                                  </span>
                                  <span className="text-xs text-muted-foreground">
                                    HP: {layer.object.survivor.health}
                                  </span>
                                </>
                              )}

                              {layer.object.oneofKind === "rubble" && (
                                <>
                                  <span className="text-xs text-muted-foreground">
                                    Energy: {layer.object.rubble?.energyRequired ?? 0}
                                  </span>
                                  <span className="text-xs text-muted-foreground">
                                    Num: {layer.object.rubble?.agentsRequired ?? 0}
                                  </span>
                                </>
                              )}
                            </AnimatedContainer>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}
    </div>
  )
}
