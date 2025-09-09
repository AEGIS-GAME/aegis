import {
  type Edge,
  attachClosestEdge,
  extractClosestEdge,
} from "@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge"
import { combine } from "@atlaskit/pragmatic-drag-and-drop/combine"
import {
  draggable,
  dropTargetForElements,
} from "@atlaskit/pragmatic-drag-and-drop/element/adapter"
import { preserveOffsetOnSource } from "@atlaskit/pragmatic-drag-and-drop/element/preserve-offset-on-source"
import { setCustomNativeDragPreview } from "@atlaskit/pragmatic-drag-and-drop/element/set-custom-native-drag-preview"
import { schema } from "aegis-schema"
import { useEffect, useRef, useState } from "react"
import { createPortal } from "react-dom"
import { getObjectId } from "./dnd-utils"
import Layer from "./Layer"

interface ListItemProps {
  layer: schema.WorldObject
  index: number
  id: string
  onDelete: () => void
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onUpdate: (updates: any) => void
}

type TaskState =
  | { type: "idle" }
  | { type: "preview"; container: HTMLElement; rect: DOMRect }
  | { type: "is-over"; edge: Edge; rect: DOMRect }
  | { type: "dragging-left-self" }

export default function LayerItem({
  layer,
  index,
  id,
  onDelete,
  onUpdate,
}: ListItemProps): JSX.Element {
  const itemRef = useRef<HTMLDivElement | null>(null)
  const mainRef = useRef<HTMLDivElement | null>(null)
  const [state, setState] = useState<TaskState>({ type: "idle" })

  useEffect(() => {
    const mainElement = mainRef.current
    const element = itemRef.current
    if (!element || !mainElement) {
      return
    }

    return combine(
      draggable({
        element: element,
        getInitialData: () => ({ layer, id }),
        onDrop: () => {
          setState({ type: "idle" })
        },
        onGenerateDragPreview({ nativeSetDragImage, location }) {
          setCustomNativeDragPreview({
            nativeSetDragImage,
            getOffset: preserveOffsetOnSource({
              element: element,
              input: location.current.input,
            }),
            render({ container }) {
              setState({
                type: "preview",
                container,
                rect: element.getBoundingClientRect(),
              })
            },
          })
        },
      }),
      dropTargetForElements({
        element: mainElement,
        getIsSticky: () => true,
        getData: ({ element, input }) => {
          const trueId = getObjectId(layer)
          return attachClosestEdge(
            { layer, id: trueId },
            { element, input, allowedEdges: ["top", "bottom"] }
          )
        },
        canDrop({ source }) {
          if (source.data.item === null) {
            return false
          }
          return true
        },
        onDragEnter({ source, self }) {
          if (
            getObjectId(source.data.layer as schema.WorldObject) === getObjectId(layer)
          ) {
            return
          }
          const closestEdge = extractClosestEdge(self.data)
          if (!closestEdge) {
            return
          }
          setState({
            type: "is-over",
            rect: element.getBoundingClientRect(),
            edge: closestEdge,
          })
        },
        onDrag({ self, source }) {
          const closestEdge = extractClosestEdge(self.data)
          if (self.data.id === source.data.id && closestEdge) {
            return
          }
          if (!closestEdge) {
            return
          }
          const proposedChanges: TaskState = {
            type: "is-over",
            rect: element.getBoundingClientRect(),
            edge: closestEdge,
          }
          setState(proposedChanges)
        },
        onDragLeave: ({ source }) => {
          if (source.data.id === getObjectId(layer)) {
            setState({ type: "dragging-left-self" })
            return
          }
          setState({ type: "idle" })
        },
        onDrop: () => {
          setState({ type: "idle" })
        },
      })
    )
  }, [layer, id])

  return (
    <>
      {state.type === "is-over" && state.edge === "top" ? (
        <DragShadow rect={state.rect} />
      ) : null}
      <div
        ref={mainRef}
        className={state.type === "dragging-left-self" ? "hidden" : ""}
      >
        <Layer
          layer={layer}
          index={index}
          onUpdate={onUpdate}
          onDelete={onDelete}
          ref={itemRef}
        />
      </div>
      {state.type === "is-over" && state.edge === "bottom" ? (
        <DragShadow rect={state.rect} />
      ) : null}
      {state.type === "preview"
        ? createPortal(<DragPreview index={index} />, state.container)
        : null}
    </>
  )
}

function DragShadow({ rect }: { rect: DOMRect }): JSX.Element {
  return (
    <div
      style={{
        height: rect.height,
      }}
      className="w-full rounded-lg bg-blue-200/60 border-2 border-blue-400 border-dashed transition-all duration-200"
    />
  )
}

function DragPreview({ index }: { index: number }): JSX.Element {
  return (
    <div className="bg-white w-full h-full rounded-lg shadow-xl p-3 border border-gray-300 text-sm scale-105 opacity-90">
      <div className="flex items-center justify-between">
        <span className="font-medium text-gray-700">Dragging:</span>
        <span className="truncate text-gray-600">Layer {index}</span>
      </div>
    </div>
  )
}
