import { motion } from "framer-motion"
import { useEffect, useMemo, useState } from "react"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useLocalStorage } from "@/hooks/useLocalStorage"
import { Scaffold } from "@/types"
import GameCycler from "../GameCycler"
import NumberInput from "../NumberInput"
import { MultiSelect } from "../ui/multiselect"

type Props = {
  scaffold: Scaffold
}

const Aegis = ({ scaffold }: Props): JSX.Element => {
  const {
    worlds,
    agents,
    startSimulation,
    killSim,
    refreshWorldsAndAgents,
    readAegisConfig,
    config,
  } = scaffold
  const [selectedWorlds, setSelectedWorlds] = useState<string[]>([])
  const [rounds, setRounds] = useLocalStorage<number>("aegis_rounds", 0)
  const [agent, setAgent] = useLocalStorage<string>("aegis_agent", "")
  const getInitialAgentAmount = (): number => {
    const stored = localStorage.getItem("aegis_agent_amount")
    if (stored !== null) {
      try {
        return JSON.parse(stored)
      } catch {
        return config?.defaultAgentAmount ?? 1
      }
    }
    return config?.defaultAgentAmount ?? 1
  }

  const [agentAmount, setAgentAmount] = useLocalStorage<number>(
    "aegis_agent_amount",
    getInitialAgentAmount()
  )
  const [debug] = useLocalStorage<boolean>("aegis_debug_mode", false)

  useEffect(() => {
    const loadConfigForTab = async (): Promise<void> => {
      await refreshWorldsAndAgents()
      await readAegisConfig()
    }

    loadConfigForTab()
  }, [])

  const isButtonDisabled = useMemo(
    () => !selectedWorlds.length || !rounds || !agent || config === null,
    [selectedWorlds, rounds, agent, config]
  )

  const showMultiAgentOptions = config?.variableAgentAmount ?? false

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="w-full space-y-4"
    >
      {config === null && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Config Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  Failed to load config.yaml. Please check your config file and ensure
                  it&apos;s valid.
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

      <div>
        <Label className="text-xs text-muted-foreground">Worlds</Label>
        <MultiSelect
          options={worlds}
          selected={selectedWorlds}
          onChange={setSelectedWorlds}
        />
      </div>

      <div>
        <Label htmlFor="rounds" className="text-xs text-muted-foreground">
          Number of Rounds
        </Label>
        <NumberInput
          name="rounds"
          value={rounds}
          min={1}
          max={1000}
          onChange={(_, val) => setRounds(val)}
        />
      </div>

      <div>
        <Label className="text-xs text-muted-foreground">Agent</Label>
        <Select value={agent} onValueChange={(value) => setAgent(value)}>
          <SelectTrigger>
            <SelectValue placeholder="Choose an agent">
              {agent || "Select an agent"}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {agents.map((agentName) => (
              <SelectItem key={agentName} value={agentName}>
                {agentName}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {showMultiAgentOptions && (
        <div>
          <Label>Number of Agents</Label>
          <NumberInput
            name="agentAmount"
            value={agentAmount}
            min={1}
            onChange={(_, val) => setAgentAmount(val)}
          />
        </div>
      )}

      <div className="flex flex-col mt-4">
        {killSim ? (
          <Button variant="destructive" onClick={killSim}>
            Kill Game
          </Button>
        ) : (
          <Button
            onClick={async () => {
              const configLoaded = await readAegisConfig()
              if (!configLoaded) {
                return
              }

              startSimulation(
                rounds.toString(),
                agentAmount.toString(),
                selectedWorlds,
                agent,
                debug
              )
            }}
            disabled={isButtonDisabled}
            className={`${isButtonDisabled ? "cursor-not-allowed" : ""}`}
          >
            Start Up Game
          </Button>
        )}
      </div>
      <GameCycler />
    </motion.div>
  )
}

export default Aegis
