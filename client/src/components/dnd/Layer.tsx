import { schema } from "aegis-schema"
import { GripVertical, Trash2 } from "lucide-react"
import { HTMLAttributes, forwardRef } from "react"
import NumberInput from "../NumberInput"
import { Badge } from "../ui/badge"
import { Button } from "../ui/button"
import { Card, CardContent } from "../ui/card"
import { Label } from "../ui/label"
import { getLayerColor, getLayerIcon } from "./dnd-utils"

interface Props extends HTMLAttributes<HTMLDivElement> {
  layer: schema.WorldObject
  index: number
  onDelete: () => void
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onUpdate: (updates: any) => void
}

const Layer = forwardRef<HTMLDivElement, Props>(
  ({ layer, index, onDelete, onUpdate, ...rest }, ref) => {
    return (
      <Card {...rest}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div
                ref={ref}
                className="cursor-grab hover:cursor-grabbing p-1 rounded hover:bg-muted transition-colors"
              >
                <GripVertical className="w-4 h-4 text-muted-foreground" />
              </div>
              <div className="flex flex-col items-start my-3 gap-0.5">
                <span className="text-md text-muted-foreground">Layer {index}</span>
                <Badge
                  className={`${getLayerColor(layer.object.oneofKind!)} font-medium pointer-events-none`}
                >
                  {getLayerIcon(layer.object.oneofKind!)}
                  <span className="ml-1 capitalize">{layer.object.oneofKind}</span>
                </Badge>
              </div>
            </div>
            {layer.object.oneofKind === "survivor" && (
              <div className="space-y-3 pt-2">
                <div className="flex flex-col items-center gap-2">
                  <Label
                    htmlFor={`health-${index}`}
                    className="text-xs text-muted-foreground"
                  >
                    Survivor HP
                  </Label>
                  <NumberInput
                    name="health"
                    value={layer.object.survivor.health}
                    min={1}
                    max={100}
                    onChange={(_, value) => {
                      const survivor =
                        layer.object.oneofKind === "survivor"
                          ? layer.object.survivor
                          : undefined
                      if (!survivor || !onUpdate) {
                        return
                      }

                      onUpdate({
                        survivor: {
                          ...survivor,
                          health: value,
                        },
                      })
                    }}
                  />
                </div>
              </div>
            )}

            {layer.object.oneofKind === "rubble" && (
              <div className="space-y-3 pt-2">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label
                      htmlFor={`energy-${index}`}
                      className="text-xs text-muted-foreground"
                    >
                      Energy Required
                    </Label>
                    <NumberInput
                      name="energyRequired"
                      value={layer.object.rubble?.energyRequired ?? 0}
                      min={1}
                      max={999}
                      onChange={(_, value) => {
                        const rubble =
                          layer.object.oneofKind === "rubble"
                            ? layer.object.rubble
                            : undefined
                        if (!rubble || !onUpdate) {
                          return
                        }

                        onUpdate({
                          rubble: {
                            ...rubble,
                            energyRequired: value,
                          },
                        })
                      }}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label
                      htmlFor={`agents-${index}`}
                      className="text-xs text-muted-foreground"
                    >
                      Agents Required
                    </Label>
                    <NumberInput
                      name="agentsRequired"
                      value={layer.object.rubble?.agentsRequired ?? 0}
                      min={1}
                      max={10}
                      onChange={(_, value) => {
                        const rubble =
                          layer.object.oneofKind === "rubble"
                            ? layer.object.rubble
                            : undefined
                        if (!rubble || !onUpdate) {
                          return
                        }

                        onUpdate({
                          rubble: {
                            ...rubble,
                            agentsRequired: value,
                          },
                        })
                      }}
                    />
                  </div>
                </div>
              </div>
            )}
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0 hover:bg-red-50 hover:text-red-600"
              onClick={onDelete}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }
)

Layer.displayName = "Layer"

export default Layer
