import { OrbitControls } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import type * as THREE from "three";
import { formatSeconds, slowMotionFactor } from "../lib/classical";
import { buildCloudColors } from "../lib/cloudColors";
import { CLASSICAL_SLOWMO, NUCLEUS_MARKER_LIBERTY, RENDER_LIBERTIES } from "../lib/liberties";
import { nucleusCaption, nucleusSphere } from "../lib/nucleus";
import { useAppStore } from "../state/store";
import { Badge } from "./Badge";
import { GhostClock, GhostOverlay } from "./GhostOverlay";
import { Legend } from "./Legend";
import { PointCloud } from "./PointCloud";

function CameraRig({ distance }: { distance: number }) {
  const camera = useThree((s) => s.camera as THREE.PerspectiveCamera);
  useEffect(() => {
    camera.position.set(distance * 0.7, distance * 0.45, distance);
    camera.near = distance / 100;
    camera.far = distance * 100;
    camera.lookAt(0, 0, 0);
    camera.updateProjectionMatrix();
  }, [camera, distance]);
  return null;
}

function FpsMeter() {
  const setFps = useAppStore((s) => s.setFps);
  const acc = useRef({ frames: 0, t0: 0 });
  useFrame(() => {
    const a = acc.current;
    if (a.t0 === 0) a.t0 = performance.now();
    a.frames += 1;
    const now = performance.now();
    if (now - a.t0 >= 500) {
      setFps(Math.round((a.frames * 1000) / (now - a.t0)));
      a.frames = 0;
      a.t0 = now;
    }
  });
  return null;
}

export function CloudView() {
  const {
    n,
    positions,
    density,
    phase,
    colorMode,
    stateInfo,
    nucleusMode,
    ghost,
    classicalGhost,
    classicalStatus,
    setGhost,
    loadClassical,
  } = useAppStore();
  // Deep-link (?ghost=1) sets `ghost` in initial state without going through
  // setGhost, and changing n/system resets the ghost data to idle while the
  // toggle stays on. Either way, fetch when the overlay is on but data is idle.
  useEffect(() => {
    if (ghost && classicalStatus === "idle") void loadClassical();
  }, [ghost, classicalStatus, loadClassical]);
  // Live loop phase shared between the in-Canvas animation (writes each frame)
  // and the HUD clock (polls at 10 Hz) — no per-frame React renders.
  const ghostTauRef = useRef(0);
  const colors = useMemo(
    () => buildCloudColors(colorMode, density, phase),
    [colorMode, density, phase],
  );
  const distance = stateInfo
    ? Math.max(6 * stateInfo.mean_radius.value, 1e-3)
    : 5 * n * n + 3;
  const sysInfo = stateInfo?.system ?? null;
  const nucleus = nucleusSphere(
    nucleusMode,
    sysInfo?.nuclear_radius?.value ?? null,
    distance,
  );
  const caption = nucleusCaption(nucleusMode, sysInfo, nucleus);
  return (
    <div className="canvas-wrap">
      <Canvas camera={{ fov: 50 }}>
        <color attach="background" args={["#0a0e12"]} />
        <CameraRig distance={distance} />
        <FpsMeter />
        {positions && (
          <PointCloud
            positions={positions}
            pointSize={distance / 350}
            colors={colors}
          />
        )}
        {ghost && classicalGhost && (
          <GhostOverlay ghost={classicalGhost} distance={distance} tauRef={ghostTauRef} />
        )}
        {nucleus && (
          <mesh>
            <sphereGeometry args={[nucleus.radius, 32, 16]} />
            <meshBasicMaterial
              color={nucleus.kind === "marker" ? "#ffb86b" : "#ffd9a0"}
            />
          </mesh>
        )}
        <OrbitControls />
      </Canvas>
      {!positions && <p className="hint">Choose a state and press Sample</p>}
      <div className="canvas-overlay">
        <Badge provenance={RENDER_LIBERTIES} />
        {nucleus?.kind === "marker" && <Badge provenance={NUCLEUS_MARKER_LIBERTY} />}
        {caption && <span className="nucleus-caption">{caption}</span>}
        <Legend mode={colorMode} />
        <label className="ghost-toggle">
          <input
            type="checkbox"
            checked={ghost}
            onChange={(e) => setGhost(e.target.checked)}
          />
          Classical ghost
        </label>
        {ghost && classicalStatus === "sampling" && (
          <span className="ghost-readout">loading classical orbits…</span>
        )}
        {ghost && classicalGhost && (
          <div className="ghost-hud">
            <div className="ghost-banner">
              Counterfactual — a classical electron would spiral in; real atoms do not
            </div>
            <GhostClock
              tauRef={ghostTauRef}
              collapseSeconds={classicalGhost.collapse_time_s.value}
            />
            <div className="ghost-readout">
              collapse in {formatSeconds(classicalGhost.collapse_time_s.value)}{" "}
              <Badge provenance={classicalGhost.collapse_time_s.provenance} />
            </div>
            <div className="ghost-readout">
              {Math.round(classicalGhost.orbit_count.value).toLocaleString()} orbits before
              collapse <Badge provenance={classicalGhost.orbit_count.provenance} />
            </div>
            <div className="ghost-readout">
              shown at ~{slowMotionFactor(classicalGhost.collapse_time_s.value).toExponential(1)}×
              slow motion <Badge provenance={CLASSICAL_SLOWMO} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
