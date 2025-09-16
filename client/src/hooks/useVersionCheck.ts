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
  const [refreshTrigger, setRefreshTrigger] = useState(0)

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

        // If we can't get local version, show error banner
        if (!localVersion) {
          setVersionInfo({
            localVersion: null,
            latestVersion: null,
            updateAvailable: true, // Show banner for unknown version
            isLoading: false,
            error:
              "Version unknown - please run aegis init again or set your aegis path to the correct project location",
          })
          return
        }

        const response = await fetch(
          "https://api.github.com/repos/AEGIS-GAME/aegis/releases/latest"
        )
        if (!response.ok) {
          throw new Error("Failed to fetch latest version")
        }

        const release = await response.json()
        const latestVersion =
          release.tag_name?.replace("v", "").replace("client-", "") || null

        // Normalize both versions for comparison
        const normalizeVersion = (version: string | null): string => {
          if (!version) {
            return ""
          }
          return version.replace("v", "").replace("client-", "")
        }

        const compareVersions = (a: string, b: string): number => {
          const aParts = a.split(".").map(Number)
          const bParts = b.split(".").map(Number)

          for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
            const aPart = aParts[i] || 0
            const bPart = bParts[i] || 0

            if (aPart < bPart) {
              return -1
            }
            if (aPart > bPart) {
              return 1
            }
          }

          return 0
        }

        const normalizedLocalVersion = normalizeVersion(localVersion)
        const normalizedLatestVersion = normalizeVersion(latestVersion)

        const isUpdateAvailable = Boolean(
          normalizedLatestVersion &&
            normalizedLocalVersion &&
            compareVersions(normalizedLocalVersion, normalizedLatestVersion) < 0
        )

        setVersionInfo({
          localVersion: normalizedLocalVersion || localVersion,
          latestVersion: normalizedLatestVersion || latestVersion,
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
  }, [refreshTrigger])

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent): void => {
      if (e.key === "aegisPath") {
        setRefreshTrigger((prev) => prev + 1)
      }
    }

    window.addEventListener("storage", handleStorageChange)

    return () => {
      window.removeEventListener("storage", handleStorageChange)
    }
  }, [])

  useEffect(() => {
    const handleAegisPathChange = (): void => {
      setRefreshTrigger((prev) => prev + 1)
    }

    window.addEventListener("aegisPathSet", handleAegisPathChange)

    return () => {
      window.removeEventListener("aegisPathSet", handleAegisPathChange)
    }
  }, [])

  return versionInfo
}
