import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useState } from "react"

import Round from "@/core/Round"
import { Vector } from "@/types"
import { isEqual } from "lodash"
import { MapPin, Save } from "lucide-react"
import { Badge } from "../ui/badge"
import { Button } from "../ui/button"
import LayerList from "./LayerList"

interface Props {
  tile: Vector | undefined
  round: Round | undefined
  onClose: () => void
}

export default function LayerEditor({
  tile,
  round,
  onClose,
}: Props): JSX.Element | null {
  if (!tile || !round) {
    return null
  }

  const originalLayers = round.world.cellAt(tile.x, tile.y).layers
  const [layers, setLayers] = useState([...originalLayers])
  const [hasChanges, setHasChanges] = useState(false)

  const handleSave = (): void => {
    round.world.cellAt(tile.x, tile.y).layers = [...layers]
    setHasChanges(false)
    onClose()
  }

  const handleCancel = (): void => {
    if (hasChanges) {
      setLayers([...originalLayers])
    }
    onClose()
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const updateLayer = (index: number, updates: any): void => {
    setLayers((prev) => {
      const current = prev[index]
      const updatedObject = {
        ...current.object,
        ...updates,
      }

      const next = [...prev]
      next[index] = {
        ...current,
        object: updatedObject,
      }

      const original = originalLayers[index]

      if (
        original &&
        isEqual(updatedObject, original.object) &&
        isEqual(
          next.map((l) => l.object),
          originalLayers.map((l) => l.object)
        )
      ) {
        setHasChanges(false) // state is back to original
      } else {
        setHasChanges(true) // modified from original
      }

      return next
    })
  }

  const deleteLayer = (index: number): void => {
    setLayers((prev) => prev.filter((_, i) => i !== index))
    setHasChanges(true)
  }

  return (
    <Dialog open={!!tile} onOpenChange={(open) => !open && handleCancel()}>
      <DialogContent className="max-w-lg max-h-[90vh] flex flex-col">
        <DialogHeader className="pb-4">
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-blue-600" />
            <DialogTitle className="text-lg">Layers Editor</DialogTitle>
          </div>
          <DialogDescription className="flex items-center gap-2">
            <span>
              Position: ({tile.x}, {tile.y})
            </span>
          </DialogDescription>
        </DialogHeader>
        <LayerList
          layers={layers}
          originalLayers={originalLayers}
          setLayers={setLayers}
          setHasChanges={setHasChanges}
          updateLayer={updateLayer}
          deleteLayer={deleteLayer}
        />
        <div className="flex justify-between items-center pt-4">
          <div className="flex items-center gap-2">
            {hasChanges && (
              <Badge variant="outline" className="text-yellow-600 border-yellow-300">
                Unsaved changes
              </Badge>
            )}
          </div>
          <div className="flex gap-2">
            <Button size="sm" onClick={handleSave} disabled={!hasChanges}>
              <Save className="w-4 h-4 mr-1" />
              Save Changes
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
