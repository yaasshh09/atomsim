import { describe, expect, it } from "vitest";
import { allowedSpan, clampParam, defaultParams, PRESET_PARAMS } from "./forceLaw";

describe("forceLaw preset specs", () => {
  it("every slider preset has params with defaults in range (custom has none)", () => {
    for (const [preset, specs] of Object.entries(PRESET_PARAMS)) {
      if (preset === "custom") {
        expect(specs.length).toBe(0);
        continue;
      }
      expect(specs.length).toBeGreaterThan(0);
      for (const s of specs) expect(s.default).toBeGreaterThanOrEqual(s.min);
    }
  });

  it("defaultParams returns the spec defaults", () => {
    expect(defaultParams("yukawa")).toEqual({ lambda: 3 });
    expect(defaultParams("finitewell")).toEqual({ v0: 2, a: 3 });
  });

  it("clampParam bounds to the spec range", () => {
    const spec = PRESET_PARAMS.yukawa[0];
    expect(clampParam(spec, 999)).toBe(spec.max);
    expect(clampParam(spec, -1)).toBe(spec.min);
  });

  it("allowedSpan finds the E>V window", () => {
    const r = [1, 2, 3, 4, 5];
    const v = [-10, -8, -6, -4, -2];
    expect(allowedSpan(r, v, -5)).toEqual([1, 3]); // V<-5 at r=1,2,3
    expect(allowedSpan(r, v, -20)).toBeNull(); // E below the whole well
  });
});

import { DEFAULT_EXPR, validateExprClient } from "./forceLaw";

describe("custom V(r) client validation", () => {
  it("accepts a simple expression and exposes the default", () => {
    expect(validateExprClient("-1/r")).toBeNull();
    expect(DEFAULT_EXPR).toBe("-1/r");
  });

  it("rejects empty, too-long, and unbalanced parentheses", () => {
    expect(validateExprClient("")).not.toBeNull();
    expect(validateExprClient("r".repeat(201))).not.toBeNull();
    expect(validateExprClient("exp(-r")).not.toBeNull();
  });
});
