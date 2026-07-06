import { describe, expect, it } from "vitest";
import { decodePositions } from "./client";

describe("decodePositions", () => {
  it("decodes interleaved xyz float32", () => {
    const src = new Float32Array([1, 2, 3, 4, 5, 6]);
    const out = decodePositions(src.buffer);
    expect(out).toHaveLength(6);
    expect(out[4]).toBe(5);
  });
  it("rejects buffers that are not whole xyz triplets", () => {
    expect(() => decodePositions(new ArrayBuffer(10))).toThrow(/multiple of 12/);
  });
});
