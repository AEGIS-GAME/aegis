import { motion } from "framer-motion"
import { Bug, Folder, Settings as SettingsIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { useLocalStorage } from "@/hooks/useLocalStorage"
import { Scaffold } from "@/types"
import { useEffect } from "react"

type Props = {
  scaffold: Scaffold
}

const Settings = ({ scaffold }: Props): JSX.Element => {
  const { aegisPath, setupAegisPath, readAegisConfig, config } = scaffold
  const [debugMode, setDebugMode] = useLocalStorage<boolean>("aegis_debug_mode", false)
  useEffect(() => {
    const loadConfigForTab = async (): Promise<void> => {
      await readAegisConfig()
    }

    loadConfigForTab()
  }, [])

  const renderConfigValue = (value: unknown): JSX.Element => {
    if (typeof value === "boolean") {
      return (
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            value ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
          }`}
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

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="w-full"
    >
      <div className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Folder className="w-6 h-6" />
            <h2 className="text-lg font-semibold">Aegis Path</h2>
          </div>
          <p className="text-sm border-gray-400 border p-2 rounded break-words">
            {aegisPath || "No path configured"}
          </p>
          <Button onClick={setupAegisPath} className="w-full">
            Reconfigure Aegis Path
          </Button>
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <SettingsIcon className="w-6 h-6" />
            <h2 className="text-lg font-semibold">Configuration</h2>
          </div>
          {config ? (
            <>
              <div className="text-xs text-muted-foreground">Read from config.yaml</div>
              <div className="space-y-3 p-3 bg-gray-50 rounded-lg border">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      Config Type
                    </span>
                    {renderConfigValue(config.configType)}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      Variable Agent Amount
                    </span>
                    {renderConfigValue(config.variableAgentAmount)}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      {config.variableAgentAmount ? "Max" : ""} Agent Amount
                    </span>
                    {renderConfigValue(config.defaultAgentAmount)}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      Agent Types
                    </span>
                    {renderConfigValue(config.allowAgentTypes)}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Config Error</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>
                      Failed to load config.yaml. Please check your config file and
                      ensure it&apos;s valid.
                    </p>
                  </div>
                  <div className="mt-4">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        readAegisConfig()
                      }}
                    >
                      Retry Load Config
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Bug className="w-6 h-6" />
            <h2 className="text-lg font-semibold">Debug Mode</h2>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Enable Debug Mode</Label>
              <p className="text-xs text-muted-foreground">Enables detailed logs</p>
            </div>
            <Switch checked={debugMode} onCheckedChange={setDebugMode} />
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default Settings
