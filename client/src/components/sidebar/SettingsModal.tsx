import { Button } from "@/components/ui/button"
import { ErrorMessage } from "@/components/ui/error-message"
import { Label } from "@/components/ui/label"
import { Modal } from "@/components/ui/modal"
import { Switch } from "@/components/ui/switch"
import { useLocalStorage } from "@/hooks/useLocalStorage"
import { useVersionCheck } from "@/hooks/useVersionCheck"
import { aegisAPI } from "@/services/aegis-api"
import { Scaffold } from "@/types"
import { Bug, Folder, Info, SlidersHorizontal } from "lucide-react"
import { useEffect, useState } from "react"

type Tab = "aegis" | "config" | "user" | "about"

interface Props {
  isOpen: boolean
  onClose: () => void
  scaffold: Scaffold
}

export default function SettingsModal({
  isOpen,
  onClose,
  scaffold,
}: Props): JSX.Element {
  const { aegisPath, setupAegisPath, readAegisConfig, config, updateConfigValue } =
    scaffold
  const [debugMode, setDebugMode] = useLocalStorage<boolean>("aegis_debug_mode", false)
  const [activeTab, setActiveTab] = useState<Tab>("aegis")
  const { localVersion } = useVersionCheck()

  useEffect(() => {
    if (aegisPath) {
      readAegisConfig()
    }
  }, [aegisPath, readAegisConfig])

  const renderConfigValue = (value: unknown): JSX.Element => {
    if (typeof value === "boolean") {
      return (
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
        >
          {value ? "Enabled" : "Disabled"}
        </span>
      )
    }
    if (typeof value === "number") {
      return (
        <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
          {value}
        </span>
      )
    }
    if (typeof value === "string") {
      return (
        <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
          {value}
        </span>
      )
    }
    return (
      <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-600">
        {String(value)}
      </span>
    )
  }

  const handleHiddenMoveCostsChange = async (checked: boolean): Promise<void> => {
    if (!config) {
      return
    }

    try {
      const success = await updateConfigValue("features.HIDDEN_MOVE_COSTS", checked)
      if (!success) {
        console.error("Failed to update config")
      }
    } catch (error) {
      console.error("Error updating config:", error)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Settings"
      className="min-w-[50vw] min-h-[40vh] overflow-hidden"
    >
      <div className="flex h-[40vh]">
        <div className="flex flex-col w-48 pr-2 pt-2">
          <button
            className={`flex items-center gap-2 p-2 mb-1 rounded ${activeTab === "aegis" ? "bg-muted shadow-sm" : "hover:bg-gray-100"}`}
            onClick={() => setActiveTab("aegis")}
          >
            <Folder size={16} /> Aegis Path
          </button>
          <button
            className={`flex items-center gap-2 p-2 mb-1 rounded ${activeTab === "config" ? "bg-muted shadow-sm" : "hover:bg-gray-100"}`}
            onClick={() => setActiveTab("config")}
          >
            <SlidersHorizontal size={16} /> Configuration
          </button>
          <button
            className={`flex items-center gap-2 p-2 mb-1 rounded ${activeTab === "user" ? "bg-muted shadow-sm" : "hover:bg-gray-100"}`}
            onClick={() => setActiveTab("user")}
          >
            <Bug size={16} /> User Settings
          </button>
          <button
            className={`flex items-center gap-2 p-2 mb-1 rounded ${activeTab === "about" ? "bg-muted shadow-sm" : "hover:bg-gray-100"}`}
            onClick={() => setActiveTab("about")}
          >
            <Info size={16} /> About
          </button>
        </div>

        <div className="w-px flex bg-zinc-300" />

        <div className="flex-1 overflow-auto scrollbar px-4 py-3">
          {activeTab === "aegis" && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold border-b border-zinc-300 -ml-4 pl-4 pb-2 mr-0">
                Aegis Path
              </h2>
              <p className="text-sm border-gray-300 border p-3 rounded break-words bg-gray-50">
                {aegisPath || "No path configured"}
              </p>
              <Button onClick={setupAegisPath} className="w-full">
                Reconfigure Aegis Path
              </Button>
            </div>
          )}

          {activeTab === "config" && (
            <div className="space-y-4">
              {config ? (
                <div>
                  <h2 className="text-lg font-semibold border-b border-zinc-300 -ml-4 pl-4 pb-2 mr-0">
                    Configuration
                  </h2>
                  <div className="mt-2 space-y-3 bg-gray-50 rounded-lg p-4">
                    <div className="flex justify-between">
                      <span>Config Type</span>
                      {renderConfigValue(config.configType)}
                    </div>
                    <div className="flex justify-between">
                      <span>Variable Agent Amount</span>
                      {renderConfigValue(config.variableAgentAmount)}
                    </div>
                    <div className="flex justify-between">
                      <span>{config.allowAgentTypes ? "Max" : ""} Agent Amount</span>
                      {renderConfigValue(config.defaultAgentAmount)}
                    </div>
                    <div className="flex justify-between">
                      <span>Agent Types</span>
                      {renderConfigValue(config.allowAgentTypes)}
                    </div>
                    <div className="flex justify-between">
                      <span>Hidden Move Costs</span>
                      {renderConfigValue(config.hiddenMoveCosts)}
                    </div>
                    <div className="flex justify-between">
                      <span>Versus Mode</span>
                      {renderConfigValue(config.configType === "competition")}
                    </div>
                  </div>
                </div>
              ) : (
                <ErrorMessage
                  title="Config Error"
                  message="Failed to load config.yaml. Check your config file or aegis path."
                  actionText="Retry Load Config"
                  onAction={readAegisConfig}
                />
              )}
            </div>
          )}

          {activeTab === "user" && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold border-b border-zinc-300 -ml-4 pl-4 pb-2 mr-0">
                User Settings
              </h2>
              <div className="flex items-center justify-between mt-2">
                <div>
                  <Label>Enable Debug Mode</Label>
                  <p className="text-xs text-muted-foreground">Toggle agent logs</p>
                </div>
                <Switch checked={debugMode} onCheckedChange={setDebugMode} />
              </div>
              {config?.configType === "path-assignment" && (
                <div className="flex items-center justify-between mt-2">
                  <div>
                    <Label>Enable Move Cost</Label>
                    <p className="text-xs text-muted-foreground">
                      Toggle move cost visibility
                    </p>
                  </div>
                  <Switch
                    checked={config?.hiddenMoveCosts ?? false}
                    onCheckedChange={handleHiddenMoveCostsChange}
                  />
                </div>
              )}
            </div>
          )}

          {activeTab === "about" && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold border-b border-zinc-300 -ml-4 pl-4 pb-2 mr-0">
                About AEGIS
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Version</span>
                  <span className="px-2 py-1 rounded text-sm font-medium bg-blue-100 text-blue-800">
                    {localVersion || "Unknown"}
                  </span>
                </div>
                <div className="text-sm text-muted-foreground">
                  <p>AEGIS is a survivor simulation game for educational purposes.</p>
                  <p className="mt-2">
                    Built with Electron, React, TypeScript, and Python.
                  </p>
                </div>
                <div className="pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      if (aegisAPI?.openExternal) {
                        aegisAPI.openExternal("https://github.com/AEGIS-GAME/aegis")
                      } else {
                        window.open("https://github.com/AEGIS-GAME/aegis", "_blank")
                      }
                    }}
                    className="w-full"
                  >
                    View on GitHub
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Modal>
  )
}
