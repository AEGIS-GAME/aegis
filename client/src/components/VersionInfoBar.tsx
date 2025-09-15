import { useVersionCheck } from "@/hooks/useVersionCheck"
import { AlertCircle, Download, X } from "lucide-react"
import { useState } from "react"

export default function VersionInfoBar(): JSX.Element | null {
  const { localVersion, latestVersion, updateAvailable, isLoading, error } =
    useVersionCheck()
  const [dismissed, setDismissed] = useState(false)

  if (isLoading || error || !updateAvailable || dismissed) {
    return null
  }

  const handleUpdateClick = (): void => {
    window.open("https://github.com/AEGIS-GAME/aegis/releases/latest", "_blank")
  }

  const handleDismiss = (): void => {
    setDismissed(true)
  }

  return (
    <div className="bg-blue-600 text-white px-4 py-2 flex items-center justify-between text-sm">
      <div className="flex items-center gap-2">
        <AlertCircle className="h-4 w-4" />
        <span>
          Update available: {localVersion} → {latestVersion}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={handleUpdateClick}
          className="flex items-center gap-1 px-2 py-1 bg-blue-700 hover:bg-blue-800 rounded text-xs transition-colors"
        >
          <Download className="h-3 w-3" />
          Update
        </button>
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
