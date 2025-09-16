import { useVersionCheck } from "@/hooks/useVersionCheck"
import { AlertCircle, X } from "lucide-react"
import { useState } from "react"

export default function VersionInfoBar(): JSX.Element | null {
  const { localVersion, latestVersion, updateAvailable, isLoading, error } =
    useVersionCheck()
  const [dismissed, setDismissed] = useState(false)

  if (isLoading || !updateAvailable || dismissed) {
    return null
  }

  const handleDismiss = (): void => {
    setDismissed(true)
  }

  // Show error banner for unknown version
  if (error) {
    return (
      <div className="bg-red-600 text-white px-4 py-2 flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleDismiss}
            className="p-1 hover:bg-red-700 rounded transition-colors"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-blue-600 text-white px-4 py-2 flex items-center justify-between text-sm">
      <div className="flex items-center gap-2">
        <AlertCircle className="h-4 w-4" />
        <span>
          Client Update available: {localVersion} → {latestVersion}. Run{" "}
          <span className="font-bold">aegis update</span> to update, or reset aegis path
          if this is a new project location.
        </span>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={handleDismiss}
          className="p-1 hover:bg-blue-700 rounded transition-colors"
        >
          <X className="h-3 w-3" />
        </button>
      </div>
    </div>
  )
}
