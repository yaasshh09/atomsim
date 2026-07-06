import { describe, expect, it } from "vitest";
import { clampState, isValidState, stateLabel } from "./quantum";

describe("isValidState", () => {
  it("accepts physical states", () => {
    expect(isValidState(1, 0, 0)).toBe(true);
    expect(isValidState(2, 1, -1)).toBe(true);
    expect(isValidState(6, 5, 5)).toBe(true);
  });
  it("rejects unphysical states", () => {
    expect(isValidState(1, 1, 0)).toBe(false); // l == n
    expect(isValidState(3, 1, 2)).toBe(false); // |m| > l
    expect(isValidState(0, 0, 0)).toBe(false); // n < 1
    expect(isValidState(2, -1, 0)).toBe(false);
    expect(isValidState(1.5, 0, 0)).toBe(false); // non-integer
  });
});

describe("clampState", () => {
  it("clamps l and m when n shrinks", () => {
    expect(clampState(1, 2, -2)).toEqual({ n: 1, l: 0, m: 0 });
  });
  it("clamps m into [-l, l]", () => {
    expect(clampState(3, 1, 5)).toEqual({ n: 3, l: 1, m: 1 });
  });
  it("keeps valid states unchanged", () => {
    expect(clampState(4, 2, -2)).toEqual({ n: 4, l: 2, m: -2 });
  });
});

describe("stateLabel", () => {
  it("uses spectroscopic letters", () => {
    expect(stateLabel(1, 0, 0)).toBe("1s (m = 0)");
    expect(stateLabel(2, 1, 0)).toBe("2p (m = 0)");
    expect(stateLabel(3, 2, -1)).toBe("3d (m = -1)");
  });
});
