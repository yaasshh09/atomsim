// Mirrors src/atomsim/server/schemas.py exactly — the single canonical JSON contract.

export type Fidelity =
  | "exact"
  | "numerical"
  | "approximation"
  | "counterfactual"
  | "visual_liberty";

export interface Provenance {
  fidelity: Fidelity;
  method: string;
  assumptions: string[];
  error_estimate: number | null;
  refinement: string | null;
}

export interface Quantity {
  value: number;
  unit: string;
  label: string;
  provenance: Provenance;
}

export interface StateResponse {
  n: number;
  l: number;
  m: number;
  energy: Quantity;
  energy_ev: Quantity;
  mean_radius: Quantity;
}

export type JobStatus = "pending" | "running" | "done" | "error";

export interface JobInfo {
  id: string;
  status: JobStatus;
  progress: number;
  error: string | null;
}

export interface SampleMeta {
  count: number;
  dtype: string;
  layout: string;
  unit: string;
  n: number;
  l: number;
  m: number;
  provenance: Provenance;
}
