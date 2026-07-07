import { CloudView } from "./components/CloudView";
import { Controls } from "./components/Controls";
import { InfoPanel } from "./components/InfoPanel";
import { PlaneView } from "./components/PlaneView";
import { useAppStore } from "./state/store";

export default function App() {
  const view = useAppStore((s) => s.view);
  return (
    <div className="app-grid">
      <InfoPanel />
      <main className="center-col">
        {view === "cloud" && <CloudView />}
        {view === "plane" && <PlaneView />}
      </main>
      <Controls />
    </div>
  );
}
