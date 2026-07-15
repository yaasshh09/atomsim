/* Deep links = the demo-script hook surface (spec M4): every app state the
 * Phase 2 guided tour needs is addressable by URL alone. Parsing validates
 * hard — a junk parameter is dropped, never propagated into the store. */
import type { Basis, PlaneQuantity } from "../api/client";
import type { ColorMode, ViewMode } from "../state/store";
import type { NucleusMode } from "./nucleus";
import { clampState } from "./quantum";
import { ALPHA_MAX, REAL_ALPHA } from "./whatif";

export interface UrlState {
  n: number;
  l: number;
  m: number;
  system: string;
  basis: Basis;
  view: ViewMode;
  colorMode: ColorMode;
  fineStructure: boolean;
  nucleusMode: NucleusMode;
  planeQuantity: PlaneQuantity;
  labAlpha: number;
  labZ: number;
}

export const URL_DEFAULTS: UrlState = {
  n: 1,
  l: 0,
  m: 0,
  system: "h",
  basis: "complex",
  view: "cloud",
  colorMode: "solid",
  fineStructure: false,
  nucleusMode: "marker",
  planeQuantity: "density",
  labAlpha: REAL_ALPHA,
  labZ: 1,
};

// mirrors the n select in Controls (N_CHOICES max)
const N_MAX_UI = 6;

const VIEWS: ViewMode[] = ["cloud", "plane", "radial", "levels", "spectrum", "whatif"];
const COLORS: ColorMode[] = ["solid", "density", "phase"];
const BASES: Basis[] = ["complex", "real"];
const NUCLEUS: NucleusMode[] = ["hidden", "true-scale", "marker"];
const PLANES: PlaneQuantity[] = ["density", "psi"];
const SYSTEM_KEY = /^[a-z0-9+-]{1,16}$/;

function pickEnum<T extends string>(raw: string | null, allowed: T[]): T | undefined {
  return allowed.includes(raw as T) ? (raw as T) : undefined;
}

function pickInt(raw: string | null): number | undefined {
  if (raw === null || !/^-?\d+$/.test(raw)) return undefined;
  return Number(raw);
}

function pickFloat(raw: string | null): number | undefined {
  if (raw === null || !/^-?\d*\.?\d+(e-?\d+)?$/i.test(raw)) return undefined;
  const v = Number(raw);
  return Number.isFinite(v) ? v : undefined;
}

/** Validated partial state from a query string; invalid params are dropped. */
export function parseAppUrl(search: string): Partial<UrlState> {
  const q = new URLSearchParams(search);
  const out: Partial<UrlState> = {};

  const n = pickInt(q.get("n"));
  const l = pickInt(q.get("l"));
  const m = pickInt(q.get("m"));
  if (n !== undefined || l !== undefined || m !== undefined) {
    const clamped = clampState(
      Math.min(n ?? URL_DEFAULTS.n, N_MAX_UI),
      l ?? URL_DEFAULTS.l,
      m ?? URL_DEFAULTS.m,
    );
    out.n = clamped.n;
    out.l = clamped.l;
    out.m = clamped.m;
  }

  const system = q.get("system");
  if (system !== null && SYSTEM_KEY.test(system)) out.system = system;

  const basis = pickEnum(q.get("basis"), BASES);
  if (basis) out.basis = basis;
  const view = pickEnum(q.get("view"), VIEWS);
  if (view) out.view = view;
  let color = pickEnum(q.get("color"), COLORS);
  // mirror of the store guard: phase needs the complex basis
  if (color === "phase" && (basis ?? URL_DEFAULTS.basis) === "real") color = "density";
  if (color) out.colorMode = color;
  const nucleus = pickEnum(q.get("nucleus"), NUCLEUS);
  if (nucleus) out.nucleusMode = nucleus;
  const plane = pickEnum(q.get("plane"), PLANES);
  if (plane) out.planeQuantity = plane;

  const fs = q.get("fs");
  if (fs === "1" || fs === "true") out.fineStructure = true;
  else if (fs === "0" || fs === "false") out.fineStructure = false;

  const alpha = pickFloat(q.get("alpha"));
  if (alpha !== undefined && alpha > 0) out.labAlpha = Math.min(alpha, ALPHA_MAX);
  const z = pickInt(q.get("z"));
  if (z !== undefined) out.labZ = Math.min(Math.max(z, 1), 10);

  return out;
}

/** Canonical query string for a state; default values are omitted ("" if all default). */
export function serializeAppUrl(state: UrlState): string {
  const q = new URLSearchParams();
  if (state.n !== URL_DEFAULTS.n) q.set("n", String(state.n));
  if (state.l !== URL_DEFAULTS.l) q.set("l", String(state.l));
  if (state.m !== URL_DEFAULTS.m) q.set("m", String(state.m));
  if (state.system !== URL_DEFAULTS.system) q.set("system", state.system);
  if (state.basis !== URL_DEFAULTS.basis) q.set("basis", state.basis);
  if (state.view !== URL_DEFAULTS.view) q.set("view", state.view);
  if (state.colorMode !== URL_DEFAULTS.colorMode) q.set("color", state.colorMode);
  if (state.fineStructure !== URL_DEFAULTS.fineStructure) q.set("fs", "1");
  if (state.nucleusMode !== URL_DEFAULTS.nucleusMode) q.set("nucleus", state.nucleusMode);
  if (state.planeQuantity !== URL_DEFAULTS.planeQuantity) q.set("plane", state.planeQuantity);
  if (Math.abs(state.labAlpha - URL_DEFAULTS.labAlpha) > 1e-9) {
    q.set("alpha", String(state.labAlpha));
  }
  if (state.labZ !== URL_DEFAULTS.labZ) q.set("z", String(state.labZ));
  // note: '+' stays percent-encoded (%2B) — a literal '+' in a query string
  // reads back as a space, which would break the he+ round-trip
  const s = q.toString();
  return s ? `?${s}` : "";
}
