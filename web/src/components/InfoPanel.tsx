import { useEffect } from "react";
import { stateLabel } from "../lib/quantum";
import { useAppStore } from "../state/store";
import { Badge } from "./Badge";

export function InfoPanel() {
  const { n, l, m, stateInfo, meta, loadStateInfo } = useAppStore();
  useEffect(() => {
    void loadStateInfo();
  }, [n, l, m, loadStateInfo]);
  return (
    <aside className="panel">
      <h1 className="brand">atomsim</h1>
      <h2>Hydrogen (Z = 1)</h2>
      <p className="state-label">{stateLabel(n, l, m)}</p>
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
          <dt>
            {"⟨r⟩"} <Badge provenance={stateInfo.mean_radius.provenance} />
          </dt>
          <dd>{stateInfo.mean_radius.value.toFixed(3)} a{"₀"}</dd>
          {meta && (
            <>
              <dt>
                Sampled points <Badge provenance={meta.provenance} />
              </dt>
              <dd>{meta.count.toLocaleString()}</dd>
            </>
          )}
        </dl>
      )}
    </aside>
  );
}
