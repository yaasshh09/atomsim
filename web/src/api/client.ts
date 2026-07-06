import type { JobInfo, SampleMeta, StateResponse } from "./types";

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export function getState(n: number, l: number, m: number): Promise<StateResponse> {
  return getJson(`/api/state/${n}/${l}/${m}`);
}

export async function createSampleJob(
  n: number,
  l: number,
  m: number,
  count: number,
  seed = 0,
): Promise<JobInfo> {
  const res = await fetch("/api/jobs/sample", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ n, l, m, count, seed }),
  });
  if (!res.ok) throw new Error(`sample job: HTTP ${res.status}`);
  return res.json() as Promise<JobInfo>;
}

export function watchJob(jobId: string, onProgress: (p: number) => void): Promise<void> {
  return new Promise((resolve, reject) => {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/ws/jobs/${jobId}`);
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data as string) as {
        status: string;
        progress: number;
        error: string | null;
      };
      onProgress(msg.progress);
      if (msg.status === "done") {
        ws.close();
        resolve();
      } else if (msg.status === "error") {
        ws.close();
        reject(new Error(msg.error ?? "job failed"));
      }
    };
    ws.onerror = () => reject(new Error("websocket error"));
  });
}

export function getSampleMeta(jobId: string): Promise<SampleMeta> {
  return getJson(`/api/jobs/${jobId}/meta`);
}

export async function getSampleData(jobId: string): Promise<Float32Array> {
  const res = await fetch(`/api/jobs/${jobId}/data`);
  if (!res.ok) throw new Error(`sample data: HTTP ${res.status}`);
  return decodePositions(await res.arrayBuffer());
}

export function decodePositions(buffer: ArrayBuffer): Float32Array {
  if (buffer.byteLength % 12 !== 0) {
    throw new Error(
      `positions byte length ${buffer.byteLength} is not a multiple of 12 (xyz float32)`,
    );
  }
  return new Float32Array(buffer);
}
