import GameArea from "./components/Game-area"
import ControlsBar from "./components/controls-bar/Controls-bar"
import Sidebar from "./components/sidebar/Sidebar"
import useGames from "./hooks/useGames"

export default function App(): JSX.Element {
  const games = useGames()

  return (
    <div className="flex bg-background overflow-hidden">
      <Sidebar />
      <div className="flex w-full h-screen justify-center">
        <GameArea />
        {games?.playable && <ControlsBar />}
      </div>
    </div>
  )
}
