import { scaleLinear } from "d3-scale";
import { useEffect } from "react";
import {
  ALPHA_MAX, fineErrorFraction, formatAlpha, isAltered,
  isBeyondValidity, shellSplitting,
} from "../lib/whatif";
import { useAppStore } from "../state/store";
import { Badge } from "./Badge";

const W = 720;
const H = 480;
const ZOOM_N = 2; // textbook shell: 2p3/2 - 2p1/2 split grows with alpha

export function WhatIfView() {
  const {
    labAlpha, labZ, whatif, whatifStatus, error,
    setLabAlpha, setLabZ, loadWhatIf,
  } = useAppStore();

  useEffect(() => {
    if (whatif === null && whatifStatus === "idle") void loadWhatIf();
  }, [whatif, whatifStatus, loadWhatIf]);

  if (whatifStatus === "error") return <p className="error">{error}</p>;
  if (!whatif) return <p className="hint-block">loading What-If lab…</p>;

  const { real, altered } = whatif;
  const altOn = isAltered(altered.alpha, real.alpha);
  const badgeProv = (altered.fine ?? real.fine ?? [])[0]?.shift.provenance;

  const eMin = real.gross[0].energy_ev.value;
  const y = scaleLinear([eMin, 0], [H - 40, 60]);
  const rx1 = 70;
  const rx2 = 300;

  const realFine = (real.fine ?? []).filter((f) => f.n === ZOOM_N);
  const altFine = (altered.fine ?? []).filter((f) => f.n === ZOOM_N);
  const shiftsUeV = [...realFine, ...altFine].map((f) => f.shift_ev.value * 1e6);
  const lo = Math.min(0, ...shiftsUeV);
  const hi = Math.max(0, ...shiftsUeV);
  const pad = (hi - lo || 1) * 0.2;
  const yz = scaleLinear([lo - pad, hi + pad], [H - 60, 90]);
  const columns = [
    { x: 470, rows: realFine, label: "real", cf: false },
    { x: 590, rows: altFine, label: "altered", cf: altOn },
  ];

  const errFrac = fineErrorFraction(altered.fine);
  const beyond = isBeyondValidity(altered.fine);
  const splitEv = shellSplitting(altered.fine, ZOOM_N);

  return (
    <div className="view-wrap">
      <div className="view-header">
        <span className="plot-title">
          What-If: fundamental constants{" "}
          {badgeProv && <Badge provenance={badgeProv} />}
        </span>
      </div>

      {altOn && (
        <div className="counterfactual-banner">
          COUNTERFACTUAL · α = {formatAlpha(altered.alpha)} (real {formatAlpha(real.alpha)})
        </div>
      )}

      <svg viewBox={`0 0 ${W} ${H}`} role="img" className="levels-svg">
        <text x={(rx1 + rx2) / 2} y={30} textAnchor="middle" className="tick">
          gross levels (Z={altered.system.z}) — α-independent, EXACT
        </text>
        {real.gross.map((g) => (
          <g key={g.n}>
            <line
              x1={rx1} x2={rx2}
              y1={y(g.energy_ev.value)} y2={y(g.energy_ev.value)}
              className="rung"
            />
            <text x={rx1 - 8} y={y(g.energy_ev.value)} dy="0.32em" textAnchor="end" className="tick">
              n={g.n}
            </text>
            <text x={rx2 + 8} y={y(g.energy_ev.value)} dy="0.32em" className="tick">
              2n²={g.degeneracy}
            </text>
          </g>
        ))}

        <text x={530} y={54} textAnchor="middle" className="tick">
          n={ZOOM_N} fine split [µeV] — real vs altered
        </text>
        {columns.map((col) => (
          <g key={col.label}>
            <text x={col.x + 20} y={78} textAnchor="middle" className="tick">
              {col.label}
            </text>
            {col.rows.map((f) => (
              <g key={`${col.label}-${f.l}-${f.j}`}>
                <line
                  x1={col.x} x2={col.x + 40}
                  y1={yz(f.shift_ev.value * 1e6)} y2={yz(f.shift_ev.value * 1e6)}
                  className={col.cf ? "rung rung-counterfactual" : "rung"}
                />
                <text x={col.x + 46} y={yz(f.shift_ev.value * 1e6)} dy="0.32em" className="tick">
                  j={f.j} · {(f.shift_ev.value * 1e6).toFixed(1)}
                </text>
              </g>
            ))}
          </g>
        ))}
      </svg>

      <div className="whatif-controls">
        <label>
          α = {formatAlpha(labAlpha)} ({labAlpha.toExponential(2)})
          <input
            type="range" min={0.0005} max={ALPHA_MAX} step={0.0005}
            value={labAlpha}
            onChange={(e) => setLabAlpha(Number(e.target.value))}
          />
        </label>
        <div className="stepper">
          <span>nuclear charge Z</span>
          <button type="button" onClick={() => setLabZ(Math.max(1, labZ - 1))} disabled={labZ <= 1}>
            −
          </button>
          <span>{labZ}</span>
          <button type="button" onClick={() => setLabZ(Math.min(10, labZ + 1))} disabled={labZ >= 10}>
            +
          </button>
        </div>
        <button type="button" className="primary" onClick={() => setLabAlpha(real.alpha)}>
          reset α to real
        </button>
      </div>

      <p className={beyond ? "error" : "caption"}>
        {beyond
          ? `Fine-structure error ≈ ${(errFrac * 100).toFixed(0)}% — past the perturbative model's validity. The exact Dirac solution would differ; this is the honest limit, not a glitch.`
          : `Fine-structure fractional error ≈ ${(errFrac * 100).toFixed(1)}% (grows as (Zα)²). n=${ZOOM_N} splitting: ${splitEv.toExponential(2)} eV. α never touches the gross ladder — turn it down and the accidental l-degeneracy re-fuses. Equal-j states (2s₁/₂, 2p₁/₂) stay degenerate at this order — the Lamb shift is honestly absent.`}
      </p>
    </div>
  );
}
