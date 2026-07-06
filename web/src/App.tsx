import { OrbitControls } from "@react-three/drei";
import { Canvas, useThree } from "@react-three/fiber";
import { useEffect } from "react";
import { Controls } from "./components/Controls";
import { InfoPanel } from "./components/InfoPanel";
import { PointCloud } from "./components/PointCloud";
import { useAppStore } from "./state/store";

function CameraRig({ distance }: { distance: number }) {
  const camera = useThree((s) => s.camera);
  useEffect(() => {
    camera.position.set(distance * 0.7, distance * 0.45, distance);
    camera.lookAt(0, 0, 0);
    camera.updateProjectionMatrix();
  }, [camera, distance]);
  return null;
}

export default function App() {
  const { n, positions } = useAppStore();
  return (
    <div className="app-grid">
      <InfoPanel />
      <main className="canvas-wrap">
        <Canvas camera={{ fov: 50, near: 0.1, far: 5000 }}>
          <color attach="background" args={["#0a0e12"]} />
          <CameraRig distance={5 * n * n + 3} />
          {positions && <PointCloud positions={positions} pointSize={0.02 * n * n} />}
          <OrbitControls />
        </Canvas>
        {!positions && <p className="hint">Choose a state and press Sample</p>}
      </main>
      <Controls />
    </div>
  );
}
