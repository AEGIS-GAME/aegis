import { useState } from "react"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

interface ConfirmClearDialogProps {
  onConfirm: () => void
  disabled?: boolean
}

export default function ConfirmClearDialog({
  onConfirm,
  disabled,
}: ConfirmClearDialogProps): JSX.Element {
  const [open, setOpen] = useState(false)

  const handleConfirm = (): void => {
    onConfirm()
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`text-xs text-destructive hover:text-destructive-foreground hover:bg-destructive ${disabled ? "invisible" : ""}`}
        >
          Clear
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Confirm Clear</DialogTitle>
          <DialogDescription>
            Are you sure you want to clear the world? This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button className="ml-2" variant="destructive" onClick={handleConfirm}>
            Clear
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
