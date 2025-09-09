import { autoScrollForElements } from "@atlaskit/pragmatic-drag-and-drop-auto-scroll/element"
import { extractClosestEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge"
import { reorderWithEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/util/reorder-with-edge"
import { combine } from "@atlaskit/pragmatic-drag-and-drop/combine"
import { monitorForElements } from "@atlaskit/pragmatic-drag-and-drop/element/adapter"
import { schema } from "aegis-schema"
import { isEqual } from "lodash"
import { Layers3 } from "lucide-react"
import { SetStateAction, useEffect, useRef } from "react"
import { flushSync } from "react-dom"
import { Card, CardContent } from "../ui/card"
import { getObjectId } from "./dnd-utils"
import LayerItem from "./LayerItem"

interface Props {
  layers: schema.WorldObject[]
  originalLayers: schema.WorldObject[]
  setLayers: (value: SetStateAction<schema.WorldObject[]>) => void
  setHasChanges: (value: SetStateAction<boolean>) => void
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  updateLayer: (index: number, updates: any) => void
  deleteLayer: (index: number) => void
}

export default function LayerList({
  layers,
  originalLayers,
  setLayers,
  setHasChanges,
  updateLayer,
  deleteLayer,
}: Props): JSX.Element {
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) {
      return
    }

    return combine(
      autoScrollForElements({
        element: container,
      }),
      monitorForElements({
        canMonitor({ source }) {
          return source.data?.id !== null
        },
        onDrop: ({ source, location }) => {
          const dest = location.current.dropTargets[0]
          if (!dest) {
            return
          }

          const sourceId = source.data.id as string
          const destId = dest.data.id as string
          const closestEdge = extractClosestEdge(dest.data)

          const sourceIndex = layers.findIndex(
            (layer) => getObjectId(layer) === sourceId
          )
          const destIndex = layers.findIndex((layer) => getObjectId(layer) === destId)

          flushSync(() => {
            setLayers((prev) => {
              if (sourceIndex < 0 || destIndex < 0) {
                return prev
              }
              const next = reorderWithEdge({
                list: prev,
                startIndex: sourceIndex,
                indexOfTarget: destIndex,
                closestEdgeOfTarget: closestEdge,
                axis: "vertical",
              })
              setHasChanges(!isEqual(next, originalLayers))
              return next
            })
          })
        },
      })
    )
  }, [layers, setLayers, setHasChanges, originalLayers])

  return (
    <div className="flex-1 min-h-0 overflow-y-auto" ref={containerRef}>
      <div className="flex flex-col p-2 gap-2 relative">
        {layers.length === 0 ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-8 text-center">
              <Layers3 className="w-8 h-8 text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">No layers on this tile</p>
              <p className="text-xs text-muted-foreground mt-1">
                Layers will appear here when added
              </p>
            </CardContent>
          </Card>
        ) : (
          layers.map((layer, i) => (
            <LayerItem
              key={i}
              index={i + 1}
              layer={layer}
              id={getObjectId(layer)}
              onUpdate={(updates): void => updateLayer(i, updates)}
              onDelete={(): void => deleteLayer(i)}
            />
          ))
        )}
      </div>
    </div>
  )
}
