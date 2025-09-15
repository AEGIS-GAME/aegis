import GameArea from "./components/Game-area"
import ControlsBar from "./components/controls-bar/Controls-bar"
import Sidebar from "./components/sidebar/Sidebar"
import VersionInfoBar from "./components/VersionInfoBar"
import useGames from "./hooks/useGames"

export default function App(): JSX.Element {
  const games = useGames()

  return (
    <div className="flex flex-col bg-background overflow-hidden">
      <VersionInfoBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex w-full h-full justify-center">
          <GameArea />
          {games?.playable && <ControlsBar />}
        </div>
      </div>
    </div>
  )
}
