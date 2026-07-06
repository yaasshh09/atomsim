import { useMemo } from "react";
import * as THREE from "three";

interface Props {
  positions: Float32Array;
  pointSize: number;
}

export function PointCloud({ positions, pointSize }: Props) {
  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return g;
  }, [positions]);
  return (
    // VISUAL LIBERTY: physics z (the quantization axis) is rendered screen-vertical
    // (three.js +y) so |m|-dependent structure reads at a glance; data stays xyz in bohr.
    <points geometry={geometry} rotation={[-Math.PI / 2, 0, 0]}>
      {/* VISUAL LIBERTY: point size, color, glow are presentational choices,
          not physical quantities. Disclosed in UI copy (M3 inspector). */}
      <pointsMaterial
        size={pointSize}
        sizeAttenuation
        color="#7cffb2"
        transparent
        opacity={0.35}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
