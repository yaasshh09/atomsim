import type { Provenance } from "../api/types";
import { MARKER_DIVISOR } from "./nucleus";

/** The frontend is the authority on its own rendering choices — disclosed, never hidden. */
export const RENDER_LIBERTIES: Provenance = {
  fidelity: "visual_liberty",
  method: "three.js point-sprite rendering of engine-sampled positions",
  assumptions: [
    "z quantization axis drawn screen-vertical (data stays xyz in bohr)",
    "point size, opacity and additive glow are presentation, not physics",
    "density colour brightness gamma-compressed: t = (rho/rho_max)^0.5",
  ],
  error_estimate: null,
  refinement: "positions, density and phase channels come from the engine unmodified",
};

export const NUCLEUS_MARKER_LIBERTY: Provenance = {
  fidelity: "visual_liberty",
  method: "nucleus drawn as a fixed-size marker sphere at the origin",
  assumptions: [
    `marker radius = camera distance / ${MARKER_DIVISOR} — presentation, not physics`,
    "true position (the origin) and the r_rms readout are exact",
    "switch to 'true scale' to see the honest, subpixel size",
  ],
  error_estimate: null,
  refinement: "the magnification factor is stated live in the canvas caption",
};

export const THUMBNAIL_LIBERTY: Provenance = {
  fidelity: "visual_liberty",
  method: "server-rendered inferno PNG of |psi|^2 on the y=0 plane (navigation aid)",
  assumptions: [
    "brightness gamma-compressed: t = (rho/rho_max)^0.5",
    "not a measurement surface: no axes, no scale",
  ],
  error_estimate: null,
  refinement: "open the 2D cross-section view for the labeled, scaled version",
};
