import { useMemo } from "react";
import * as THREE from "three";

interface Props {
  positions: Float32Array;
  pointSize: number;
  colors?: Float32Array | null;
}

export function PointCloud({ positions, pointSize, colors }: Props) {
  const useVertexColors = Boolean(colors && colors.length === positions.length);
  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    if (colors && colors.length === positions.length) {
      g.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    }
    return g;
  }, [positions, colors]);
  return (
    // VISUAL LIBERTY: physics z (the quantization axis) is rendered screen-vertical
    // (three.js +y) so |m|-dependent structure reads at a glance; data stays xyz in bohr.
    <points geometry={geometry} rotation={[-Math.PI / 2, 0, 0]}>
      {/* VISUAL LIBERTY: point size, colour mapping, glow are presentational choices,
          disclosed via the RENDER_LIBERTIES badge in the canvas overlay. */}
      <pointsMaterial
        size={pointSize}
        sizeAttenuation
        color={useVertexColors ? "#ffffff" : "#7cffb2"}
        vertexColors={useVertexColors}
        transparent
        opacity={useVertexColors ? 0.55 : 0.35}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
