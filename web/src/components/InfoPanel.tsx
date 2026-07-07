import { useEffect } from "react";
import { realOrbitalLabel, stateLabel } from "../lib/quantum";
import { useAppStore } from "../state/store";
import { Badge } from "./Badge";

export function InfoPanel() {
  const {
    n, l, m, basis, system, fineStructure, stateInfo, meta, fps, view, loadStateInfo,
  } = useAppStore();
  useEffect(() => {
    void loadStateInfo();
  }, [n, l, m, system, fineStructure, loadStateInfo]);
  const sys = stateInfo?.system;
  return (
    <aside className="panel">
      <h1 className="brand">atomsim</h1>
      <h2>{sys ? `${sys.name} (Z = ${sys.z})` : "…"}</h2>
      {sys && <p className="system-desc">{sys.description}</p>}
      <p className="state-label">
        {stateLabel(n, l, m)}
        {basis === "real" && (
          <span className="orbital-label"> · {realOrbitalLabel(l, m)}</span>
        )}
      </p>
      {stateInfo && (
        <dl className="readouts">
          <dt>
            Energy <Badge provenance={stateInfo.energy.provenance} />
          </dt>
          <dd>
            {stateInfo.energy.value.toFixed(6)} hartree
            <br />
            {stateInfo.energy_ev.value.toFixed(4)} eV
          </dd>
          {fineStructure && stateInfo.levels.length > 0 && (
            <>
              <dt>
                Fine structure <Badge provenance={stateInfo.levels[0].shift.provenance} />
              </dt>
              <dd>
                {stateInfo.levels.map((lev) => (
                  <span key={lev.j} className="fs-level">
                    j = {lev.j}: {(lev.shift_ev.value * 1e6).toFixed(2)} µeV
                    <br />
                  </span>
                ))}
              </dd>
            </>
          )}
          <dt>
            {"⟨r⟩"} <Badge provenance={stateInfo.mean_radius.provenance} />
          </dt>
          <dd>
            {stateInfo.mean_radius.value.toFixed(3)} a{"₀"} ·{" "}
            {stateInfo.mean_radius_pm.value.toFixed(1)} pm
          </dd>
          <dt>
            |L| <Badge provenance={stateInfo.angular_momentum.provenance} />
          </dt>
          <dd>{stateInfo.angular_momentum.value.toFixed(3)} ℏ</dd>
          <dt>Nodes</dt>
          <dd>
            {stateInfo.radial_nodes} radial · {stateInfo.angular_nodes} angular
          </dd>
          {meta && (
            <>
              <dt>
                Sampled points <Badge provenance={meta.provenance} />
              </dt>
              <dd>{meta.count.toLocaleString()}</dd>
            </>
          )}
          {view === "cloud" && fps > 0 && (
            <>
              <dt>FPS (measured)</dt>
              <dd>{fps}</dd>
            </>
          )}
        </dl>
      )}
    </aside>
  );
}
