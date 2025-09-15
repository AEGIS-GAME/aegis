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

        const localVersion = (await aegisAPI?.getAppVersion?.()) || "2.7.5"

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
          latestVersion &&
          localVersion &&
          compareVersions(latestVersion, localVersion) > 0

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

function compareVersions(version1: string, version2: string): number {
  const v1Parts: number[] = version1.split(".").map(Number)
  const v2Parts: number[] = version2.split(".").map(Number)

  const maxLength = Math.max(v1Parts.length, v2Parts.length)

  for (let i = 0; i < maxLength; i++) {
    const v1Part = v1Parts[i] || 0
    const v2Part = v2Parts[i] || 0

    if (v1Part > v2Part) {
      return 1
    } else if (v1Part < v2Part) {
      return -1
    }
  }

  return 0
}
