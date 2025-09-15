import { useEffect, useState } from "react"
import { aegisAPI } from "@/services/aegis-api"

interface VersionInfo {
  localVersion: string | null
  latestVersion: string | null
  updateAvailable: boolean
  isLoading: boolean
  error: string | null
}

export function useVersionCheck(): VersionInfo {
  const [versionInfo, setVersionInfo] = useState<VersionInfo>({
    localVersion: null,
    latestVersion: null,
    updateAvailable: false,
    isLoading: true,
    error: null,
  })

  useEffect(() => {
    const checkVersion = async (): Promise<void> => {
      try {
        await new Promise((resolve) => setTimeout(resolve, 1000))

        const aegisPath = localStorage.getItem("aegisPath")

        // Don't show banner if AEGIS path is not set up
        if (!aegisPath) {
          setVersionInfo({
            localVersion: null,
            latestVersion: null,
            updateAvailable: false,
            isLoading: false,
            error: null,
          })
          return
        }

        const localVersion = await aegisAPI?.getClientVersion?.(aegisPath)

        // If we can't get local version, don't show update banner
        if (!localVersion) {
          setVersionInfo({
            localVersion: null,
            latestVersion: null,
            updateAvailable: false,
            isLoading: false,
            error: null,
          })
          return
        }

        // Get latest version from GitHub
        const response = await fetch(
          "https://api.github.com/repos/AEGIS-GAME/aegis/releases/latest"
        )
        if (!response.ok) {
          throw new Error("Failed to fetch latest version")
        }

        const release = await response.json()
        const latestVersion =
          release.tag_name?.replace("v", "").replace("client-", "") || null

        const isUpdateAvailable =
          latestVersion && localVersion && localVersion !== latestVersion

        setVersionInfo({
          localVersion,
          latestVersion,
          updateAvailable: isUpdateAvailable,
          isLoading: false,
          error: null,
        })
      } catch (error) {
        setVersionInfo((prev) => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error.message : "Unknown error",
        }))
      }
    }

    checkVersion()
  }, [])

  return versionInfo
}
