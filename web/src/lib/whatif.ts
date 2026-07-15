import type { FineLevel } from "../api/types";

/** Mirror of the engine's CODATA fine-structure constant (src/atomsim/constants.py
 *  ALPHA), used only to position the α control and its default. The COUNTERFACTUAL
 *  banner compares the server-echoed α values, never this constant. */
export const REAL_ALPHA = 0.0072973525643;

/** α slider/URL upper bound — matches the server's (0, 0.5] validation. */
export const ALPHA_MAX = 0.5;

/** Fine-structure fractional error past which the perturbative model is untrustworthy. */
export const FINE_WARN_FRACTION = 0.1;

/** Human form of α as a reciprocal, e.g. 0.0073 -> "1/137". */
export function formatAlpha(alpha: number): string {
  if (alpha <= 0) return "0";
  return `1/${Math.round(1 / alpha)}`;
}

/** True when α departs from the real (server-echoed) value. */
export function isAltered(alpha: number, realAlpha: number): boolean {
  return Math.abs(alpha - realAlpha) > 1e-12 * realAlpha;
}

/** Max fractional fine-structure error (error_estimate / |shift|) across levels; 0 if none. */
export function fineErrorFraction(fine: FineLevel[] | null): number {
  if (!fine || fine.length === 0) return 0;
  let max = 0;
  for (const f of fine) {
    const err = f.shift.provenance.error_estimate;
    const mag = Math.abs(f.shift.value);
    if (err !== null && mag > 0) max = Math.max(max, err / mag);
  }
  return max;
}

/** Is the perturbative fine structure past its stated validity? */
export function isBeyondValidity(fine: FineLevel[] | null): boolean {
  return fineErrorFraction(fine) > FINE_WARN_FRACTION;
}

/** eV span of the fine shifts within shell n (0 if fewer than two sub-levels). */
export function shellSplitting(fine: FineLevel[] | null, n: number): number {
  const s = (fine ?? []).filter((f) => f.n === n).map((f) => f.shift_ev.value);
  if (s.length < 2) return 0;
  return Math.max(...s) - Math.min(...s);
}
