import { describe, expect, it } from "vitest";
import { URL_DEFAULTS, parseAppUrl, serializeAppUrl } from "./urlState";

describe("parseAppUrl", () => {
  it("empty search yields no overrides", () => {
    expect(parseAppUrl("")).toEqual({});
    expect(parseAppUrl("?")).toEqual({});
  });

  it("parses a full valid deep link", () => {
    const p = parseAppUrl(
      "?n=3&l=2&m=-1&system=mu-h&basis=real&view=spectrum&color=density&fs=1&nucleus=true-scale&plane=psi",
    );
    expect(p).toEqual({
      n: 3,
      l: 2,
      m: -1,
      system: "mu-h",
      basis: "real",
      view: "spectrum",
      colorMode: "density",
      fineStructure: true,
      nucleusMode: "true-scale",
      planeQuantity: "psi",
    });
  });

  it("clamps quantum numbers as a triple and caps n at the UI maximum", () => {
    expect(parseAppUrl("?n=99&l=50&m=-50")).toEqual({ n: 6, l: 5, m: -5 });
    expect(parseAppUrl("?n=2&l=5&m=3")).toEqual({ n: 2, l: 1, m: 1 });
    // partial triples merge with defaults before clamping
    expect(parseAppUrl("?l=1")).toEqual({ n: 1, l: 0, m: 0 });
  });

  it("rejects junk instead of propagating it", () => {
    expect(parseAppUrl("?view=poster")).toEqual({});
    expect(parseAppUrl("?n=abc")).toEqual({});
    expect(parseAppUrl("?system=<script>")).toEqual({});
    expect(parseAppUrl("?color=vibes&nucleus=huge&plane=cartoon&basis=vibes")).toEqual({});
  });

  it("demotes phase colour under the real basis (mirror of the store guard)", () => {
    expect(parseAppUrl("?basis=real&color=phase")).toEqual({
      basis: "real",
      colorMode: "density",
    });
  });
});

describe("serializeAppUrl", () => {
  it("omits defaults entirely", () => {
    expect(serializeAppUrl(URL_DEFAULTS)).toBe("");
  });

  it("serializes only non-default fields", () => {
    expect(
      serializeAppUrl({ ...URL_DEFAULTS, n: 2, l: 1, view: "plane", fineStructure: true }),
    ).toBe("?n=2&l=1&view=plane&fs=1");
  });

  it("round-trips through parseAppUrl", () => {
    const state = {
      n: 4,
      l: 2,
      m: 2,
      system: "he+",
      basis: "real" as const,
      view: "levels" as const,
      colorMode: "density" as const,
      fineStructure: true,
      nucleusMode: "hidden" as const,
      planeQuantity: "psi" as const,
    };
    const parsed = parseAppUrl(serializeAppUrl(state));
    expect({ ...URL_DEFAULTS, ...parsed }).toEqual(state);
  });
});
