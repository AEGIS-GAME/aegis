import { useState } from "react"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Download } from "lucide-react"

interface Props {
  onConfirm: (filename: string) => Promise<string | null>
}

export default function ExportDialog({ onConfirm }: Props): JSX.Element {
  const [open, setOpen] = useState(false)
  const [filename, setFilename] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleExport = async (): Promise<void> => {
    if (!filename.trim()) {
      return
    }

    setLoading(true)
    const result = await onConfirm(filename.trim())
    setLoading(false)

    if (result) {
      setError(result)
    } else {
      setError(null)
      setOpen(false)
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        setOpen(v)
        setError(null)
      }}
    >
      <DialogTrigger asChild>
        <Button className="flex-1 items-center h-10">
          <Download />
          Export
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Export World</DialogTitle>
          <DialogDescription>
            Enter a filename to save your current world. Don’t include the{" "}
            <code className="mr-1">.world</code>
            extension.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Label htmlFor="export-filename">Filename</Label>
          <Input
            id="export-filename"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder="Enter filename..."
            disabled={loading}
          />
          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>
        <DialogFooter className="mt-4">
          <Button onClick={handleExport} disabled={loading}>
            {loading ? "Exporting..." : "Export"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
