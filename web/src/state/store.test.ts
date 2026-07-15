import { beforeEach, describe, expect, it } from "vitest";
import { useAppStore } from "./store";

const initial = useAppStore.getState();

beforeEach(() => {
  useAppStore.setState(initial, true);
});

function pretendLoaded() {
  useAppStore.setState({
    positions: new Float32Array(3),
    density: new Float32Array(1),
    phase: new Float32Array(1),
    stateInfo: {} as never,
    plane: {} as never,
    radial: {} as never,
    levels: {} as never,
    spectrum: {} as never,
    status: "ready",
  });
}

describe("store transitions", () => {
  it("clamps quantum numbers and invalidates data", () => {
    pretendLoaded();
    useAppStore.getState().setQuantumNumbers(3, 5, -9);
    const s = useAppStore.getState();
    expect([s.n, s.l, s.m]).toEqual([3, 2, -2]);
    expect(s.positions).toBeNull();
    expect(s.plane).toBeNull();
    expect(s.radial).toBeNull();
    expect(s.status).toBe("idle");
  });

  it("system change invalidates data", () => {
    pretendLoaded();
    useAppStore.getState().setSystem("mu-h");
    const s = useAppStore.getState();
    expect(s.system).toBe("mu-h");
    expect(s.stateInfo).toBeNull();
    expect(s.spectrum).toBeNull();
  });

  it("real basis demotes phase color mode", () => {
    useAppStore.setState({ colorMode: "phase" });
    useAppStore.getState().setBasis("real");
    const s = useAppStore.getState();
    expect(s.basis).toBe("real");
    expect(s.colorMode).toBe("density");
  });

  it("complex basis keeps chosen color mode", () => {
    useAppStore.setState({ colorMode: "density" });
    useAppStore.getState().setBasis("complex");
    expect(useAppStore.getState().colorMode).toBe("density");
  });

  it("fine-structure toggle clears only energy-derived data", () => {
    pretendLoaded();
    useAppStore.getState().setFineStructure(true);
    const s = useAppStore.getState();
    expect(s.fineStructure).toBe(true);
    expect(s.stateInfo).toBeNull();
    expect(s.levels).toBeNull();
    expect(s.spectrum).toBeNull();
    expect(s.positions).not.toBeNull();
  });

  it("plane quantity toggle clears only the plane", () => {
    pretendLoaded();
    useAppStore.getState().setPlaneQuantity("psi");
    const s = useAppStore.getState();
    expect(s.planeQuantity).toBe("psi");
    expect(s.plane).toBeNull();
    expect(s.positions).not.toBeNull();
  });

  it("lab constant change clears only the what-if data, not main physics", () => {
    pretendLoaded();
    useAppStore.setState({ whatif: {} as never, whatifStatus: "ready" });
    useAppStore.getState().setLabConst({ e: 2 });
    const s = useAppStore.getState();
    expect(s.labConst.e).toBe(2);
    expect(s.labConst.hbar).toBe(1);
    expect(s.whatif).toBeNull();
    expect(s.whatifStatus).toBe("idle");
    expect(s.positions).not.toBeNull();
    expect(s.levels).not.toBeNull();
  });

  it("lab Z change clears only the what-if data", () => {
    pretendLoaded();
    useAppStore.setState({ whatif: {} as never, whatifStatus: "ready" });
    useAppStore.getState().setLabZ(3);
    const s = useAppStore.getState();
    expect(s.labZ).toBe(3);
    expect(s.whatif).toBeNull();
    expect(s.positions).not.toBeNull();
  });

  it("nucleus mode is a pure render choice: defaults to marker, clears nothing", () => {
    expect(useAppStore.getState().nucleusMode).toBe("marker");
    pretendLoaded();
    useAppStore.getState().setNucleusMode("true-scale");
    const s = useAppStore.getState();
    expect(s.nucleusMode).toBe("true-scale");
    expect(s.positions).not.toBeNull();
    expect(s.stateInfo).not.toBeNull();
  });
});
