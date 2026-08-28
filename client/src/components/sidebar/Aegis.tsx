import { useEffect, useMemo, useState } from "react"

import { AnimatedContainer } from "@/components/ui/animated-container"
import { Button } from "@/components/ui/button"
import { ErrorMessage } from "@/components/ui/error-message"
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
// import { MultiSelect } from "../ui/multiselect"

type Props = {
  scaffold: Scaffold
}

const Aegis = ({ scaffold }: Props): JSX.Element => {
  const {
    worlds,
    agents,
    predictionDatasets,
    startSimulation,
    killSim,
    refreshWorldsAndAgents,
    readAegisConfig,
    config,
  } = scaffold
  const [world, setWorld] = useState<string>("")
  // const [selectedWorlds, setSelectedWorlds] = useState<string[]>([])
  const [rounds, setRounds] = useLocalStorage<number>("aegis_rounds", 0)
  const [agent, setAgent] = useLocalStorage<string>("aegis_agent", "")
  const [predictionData, setPredictionData] = useLocalStorage<string>(
    "aegis_prediction_data",
    "symbols"
  )
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

  useEffect(() => {
    if (config?.defaultAgentAmount && !localStorage.getItem("aegis_agent_amount")) {
      setAgentAmount(config.defaultAgentAmount)
    }
  }, [config?.defaultAgentAmount, setAgentAmount])

  useEffect(() => {
    if (predictionDatasets.length > 0 && !predictionDatasets.includes(predictionData)) {
      setPredictionData(predictionDatasets[0])
    }
  }, [predictionDatasets, predictionData, setPredictionData])

  const isButtonDisabled = useMemo(
    () =>
      !world ||
      !rounds ||
      !agent ||
      config === null ||
      (config.allowAgentPredictions && !predictionDatasets.includes(predictionData)),
    [world, rounds, agent, config, predictionDatasets, predictionData]
  )

  const showMultiAgentOptions = config?.variableAgentAmount ?? false

  return (
    <AnimatedContainer className="w-full space-y-4">
      {config === null && (
        <ErrorMessage
          title="Config Error"
          message="Failed to load config.yaml. Check your config file or aegis path."
          actionText="Retry Load Config"
          onAction={readAegisConfig}
        />
      )}

      <div>
        <Label className="text-xs text-muted-foreground">Worlds</Label>
        <Select value={world} onValueChange={(value) => setWorld(value)}>
          <SelectTrigger>
            <SelectValue placeholder="Choose a world">
              {world || "Select a world"}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {worlds.map((world) => (
              <SelectItem key={world} value={world}>
                {world}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {/* <MultiSelect */}
        {/*   options={worlds} */}
        {/*   selected={selectedWorlds} */}
        {/*   onChange={setSelectedWorlds} */}
        {/* /> */}
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

      {config?.allowAgentPredictions && (
        <div>
          <Label className="text-xs text-muted-foreground">Prediction Dataset</Label>
          {predictionDatasets.length === 0 ? (
            <ErrorMessage
              title="Prediction Data Error"
              message="No prediction datasets were found in prediction_data."
            />
          ) : (
            <Select
              value={predictionData}
              onValueChange={(value) => setPredictionData(value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Choose prediction data">
                  {predictionData || "Select prediction data"}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {predictionDatasets.map((dataset) => (
                  <SelectItem key={dataset} value={dataset}>
                    {dataset}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
      )}

      {showMultiAgentOptions && (
        <div>
          <Label className="text-xs text-muted-foreground">Number of Agents</Label>
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
              const numberInputs = document.querySelectorAll('input[type="number"]')
              numberInputs.forEach((input) => {
                if (input instanceof HTMLInputElement) {
                  input.blur()
                }
              })

              const configLoaded = await readAegisConfig()
              if (!configLoaded) {
                return
              }
              startSimulation(
                rounds.toString(),
                agentAmount.toString(),
                [world],
                agent,
                config?.allowAgentPredictions ? predictionData : "",
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
    </AnimatedContainer>
  )
}

export default Aegis
