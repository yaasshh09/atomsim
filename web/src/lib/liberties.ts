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

/**
 * Max spiral windings drawn by the classical ghost overlay. The real revolution
 * count (~1e5) cannot be resolved by a sampled line or a 60 fps point — drawing
 * it would alias into noise — so the azimuthal winding count is capped for
 * display and disclosed here. Radius law, clock, and readouts stay exact.
 */
export const GHOST_DISPLAY_WINDINGS = 16;

export const CLASSICAL_SLOWMO: Provenance = {
  fidelity: "visual_liberty",
  method: "classical collapse shown in slow motion; the live clock shows real simulated time",
  assumptions: [
    "playback speed is a viewing choice, not physics",
    `spiral drawn with at most ${GHOST_DISPLAY_WINDINGS} windings — the honest revolution count is the orbits readout`,
  ],
  error_estimate: null,
  refinement: "the slow-motion factor is stated live in the ghost HUD",
};

/**
 * Screened-atom orbitals are numerical (no closed-form psi_nlm), so the 3-D
 * cloud and 2-D plane — both built from the analytic wavefunction sampler — are
 * honestly withheld rather than faked from a hydrogenic look-alike. Disclosed
 * here; the energy-side views (levels, spectrum, radial) are fully available.
 */
export const SCREENED_ORBITAL_PLACEHOLDER: Provenance = {
  fidelity: "approximation",
  method: "numerical screened orbital — no analytic psi_nlm to sample for a 3-D cloud / 2-D plane",
  assumptions: [
    "the point-cloud and cross-section samplers require the closed-form hydrogenic wavefunction",
    "the screened radial function R_nl(r) is available in the Radial view",
  ],
  error_estimate: null,
  refinement: "sampling numerical screened orbitals is a later phase",
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
