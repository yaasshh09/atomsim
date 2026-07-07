import { OrbitControls } from "@react-three/drei";
import { Canvas, useThree } from "@react-three/fiber";
import { useEffect } from "react";
import type * as THREE from "three";
import { useAppStore } from "../state/store";
import { PointCloud } from "./PointCloud";

function CameraRig({ distance }: { distance: number }) {
  const camera = useThree((s) => s.camera as THREE.PerspectiveCamera);
  useEffect(() => {
    camera.position.set(distance * 0.7, distance * 0.45, distance);
    // near/far track the system scale so muonic hydrogen (0.008 a0) and
    // Rydberg-ish n=6 (50+ a0) both frame correctly
    camera.near = distance / 100;
    camera.far = distance * 100;
    camera.lookAt(0, 0, 0);
    camera.updateProjectionMatrix();
  }, [camera, distance]);
  return null;
}

export function CloudView() {
  const { n, positions, stateInfo } = useAppStore();
  const distance = stateInfo
    ? Math.max(6 * stateInfo.mean_radius.value, 1e-3)
    : 5 * n * n + 3;
  return (
    <div className="canvas-wrap">
      <Canvas camera={{ fov: 50 }}>
        <color attach="background" args={["#0a0e12"]} />
        <CameraRig distance={distance} />
        {positions && (
          <PointCloud positions={positions} pointSize={distance / 350} />
        )}
        <OrbitControls />
      </Canvas>
      {!positions && <p className="hint">Choose a state and press Sample</p>}
    </div>
  );
}
