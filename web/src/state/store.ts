import { create } from "zustand";
import * as client from "../api/client";
import type { SampleMeta, StateResponse } from "../api/types";
import { clampState } from "../lib/quantum";

export type SampleStatus = "idle" | "sampling" | "ready" | "error";

interface AppState {
  n: number;
  l: number;
  m: number;
  count: number;
  stateInfo: StateResponse | null;
  positions: Float32Array | null;
  meta: SampleMeta | null;
  status: SampleStatus;
  progress: number;
  error: string | null;
  setQuantumNumbers: (n: number, l: number, m: number) => void;
  setCount: (count: number) => void;
  loadStateInfo: () => Promise<void>;
  sample: () => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  n: 1,
  l: 0,
  m: 0,
  count: 100_000,
  stateInfo: null,
  positions: null,
  meta: null,
  status: "idle",
  progress: 0,
  error: null,
  setQuantumNumbers: (n, l, m) => set(clampState(n, l, m)),
  setCount: (count) => set({ count }),
  loadStateInfo: async () => {
    const { n, l, m } = get();
    set({ stateInfo: await client.getState(n, l, m) });
  },
  sample: async () => {
    const { n, l, m, count } = get();
    set({ status: "sampling", progress: 0, error: null });
    try {
      const job = await client.createSampleJob(n, l, m, count);
      await client.watchJob(job.id, (progress) => set({ progress }));
      const [meta, positions] = await Promise.all([
        client.getSampleMeta(job.id),
        client.getSampleData(job.id),
      ]);
      set({ meta, positions, status: "ready", progress: 1 });
    } catch (err) {
      set({ status: "error", error: err instanceof Error ? err.message : String(err) });
    }
  },
}));
