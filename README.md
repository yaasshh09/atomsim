# atomsim

A physically rigorous, deeply customizable quantum-mechanical atom model and
visualization platform — portfolio project, teaching tool, and self-directed
physics sandbox.

![CI](https://github.com/yaasshh09/atomsim/actions/workflows/ci.yml/badge.svg)

**Prime directive: the model never quietly lies about physics.** Every quantity
carries provenance:

| Badge | Meaning |
|---|---|
| `EXACT` | Closed-form solution of the stated model |
| `NUMERICAL` | Converged numerical solution with quantified error |
| `APPROXIMATION` | Honest simplified model, assumptions stated |
| `COUNTERFACTUAL` | Deliberately altered physics, computed rigorously |
| `VISUAL LIBERTY` | Purely presentational choice, disclosed |

## Status — Phase 1 M2: engine depth

- **`atomsim serve` opens a browser app**: pick any hydrogen (n, l, m) state,
  press **Sample**, and explore a rotatable 3D Monte-Carlo point cloud of |ψ|² —
  every displayed quantity carries a clickable provenance badge (method,
  assumptions, error scale)
- Provenance system: every boundary-crossing value is a `Quantity` (scalar),
  a `Field` (array), or a container carrying its own `Provenance`
- Exact hydrogen-like physics: energies + radial wavefunctions, reduced-mass
  exact (deuterium, muonic hydrogen, positronium, He+, ...)
- Real AND complex angular bases engine-wide (chemistry p_x/d_xy orbitals vs
  L_z eigenstates — the basis choice is labeled, never hidden)
- Perturbative fine structure (spin-orbit + relativistic + Darwin) with honest
  error scales: alpha^4, nuclear recoil, and electron g-2 all quantified
- Spectral line lists with selection rules, compared against vendored NIST ASD
  reference wavelengths in CI (citation + retrieval date in-repo)
- System presets: H, D, T, muonic hydrogen, positronium, He+, generic Z
- Numerical radial solver for **arbitrary central potentials** (the engine that
  will power real atoms, screened models, and counterfactual force laws alike),
  validated against closed-form hydrogen and harmonic-oscillator solutions —
  see [docs/phase0-convergence.md](docs/phase0-convergence.md)
- Numerical energies ship with grid-halving error estimates
- Monte-Carlo sampler validated by Kolmogorov–Smirnov tests against analytic
  radial CDFs and angular moments

## Quickstart (Windows, native — no WSL)

Prerequisites: [docs/SETUP.md](docs/SETUP.md). From the **Miniforge Prompt**,
in the cloned repo:

    conda env create -f environment.yml
    conda activate atomsim
    powershell -ExecutionPolicy Bypass -File scripts\setup_web_node_modules.ps1
    cd web
    npm ci
    npm run build
    cd ..
    atomsim serve

Your browser opens the app: pick a state (n, l, m), press **Sample**, and explore
a Monte-Carlo point cloud of |ψ|² — click any provenance badge to see the method,
assumptions, and error scale behind the number it labels.

To run the validation suites:

    pytest          # physics + server (from the repo root)
    cd web && npm test   # frontend

## Roadmap

Full specification: [docs/superpowers/specs/2026-07-04-atom-sim-requirements-design.md](docs/superpowers/specs/2026-07-04-atom-sim-requirements-design.md).
Phase 1 — "Hydrogen, Honestly" — is underway
([design](docs/superpowers/specs/2026-07-05-phase1-hydrogen-honestly-design.md)):
milestones M1 (walking skeleton) and M2 (engine depth: real orbitals, fine
structure, spectra vs NIST) of 4 are done. Next: UI depth (2D density
cross-sections, poster mode, state gallery), then polish.

## License

MIT
