/* eslint-disable @typescript-eslint/no-explicit-any */
export interface ClientConfig {
  configType: "path-assignment" | "mas-assignment" | "competition" | null
  variableAgentAmount: boolean
  defaultAgentAmount: number
  allowAgentTypes: boolean
  hiddenMoveCosts: boolean
  forceMessageCooldown: boolean
}

function getNestedValue(obj: any, path: string): any {
  return path.split(".").reduce((current, key) => {
    return current && typeof current === "object" ? current[key] : undefined
  }, obj)
}

function readBoolean(configData: any, path: string, fallback: boolean): boolean {
  const value = getNestedValue(configData, path)
  return typeof value === "boolean" ? value : fallback
}

export function parseClientConfig(configData: any): ClientConfig {
  // Validate that we actually have config data
  if (!configData || typeof configData !== "object") {
    throw new Error("Config data is missing or invalid")
  }

  // Be much stricter - we need BOTH client AND features sections
  if (!configData.client || !configData.features) {
    throw new Error("Config file must have both 'client' and 'features' sections")
  }

  // Additional validation - make sure it's not just empty sections
  if (
    typeof configData.client !== "object" ||
    typeof configData.features !== "object"
  ) {
    throw new Error("Config 'client' and 'features' must be objects")
  }

  const config: ClientConfig = {
    configType: "path-assignment",
    variableAgentAmount: false,
    defaultAgentAmount: 1,
    allowAgentTypes: false,
    hiddenMoveCosts: false,
    forceMessageCooldown: false,
  }

  try {
    const configType = getNestedValue(configData, "client.CONFIG_TYPE")
    if (
      configType === "path-assignment" ||
      configType === "mas-assignment" ||
      configType === "competition"
    ) {
      config.configType = configType
    }

    const defaultAgentAmount = getNestedValue(
      configData,
      "features.DEFAULT_AGENT_AMOUNT"
    )
    if (typeof defaultAgentAmount === "number" && defaultAgentAmount > 0) {
      config.defaultAgentAmount = defaultAgentAmount
    }

    config.variableAgentAmount = readBoolean(
      configData,
      "features.ALLOW_CUSTOM_AGENT_COUNT",
      config.variableAgentAmount
    )
    config.allowAgentTypes = readBoolean(
      configData,
      "features.ALLOW_AGENT_TYPES",
      config.allowAgentTypes
    )
    config.hiddenMoveCosts = readBoolean(
      configData,
      "features.HIDDEN_MOVE_COSTS",
      config.hiddenMoveCosts
    )
    config.forceMessageCooldown = readBoolean(
      configData,
      "features.FORCE_MESSAGE_COOLDOWN",
      config.forceMessageCooldown
    )

    return config
  } catch (error) {
    throw new Error(`Failed to parse config.yaml: ${error}`)
  }
}

export function getConfigValue(configData: any, path: string): any {
  return getNestedValue(configData, path)
}
