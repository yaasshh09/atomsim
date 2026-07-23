# Phase 9 — Exact Dirac Hydrogen (design)

**Date:** 2026-07-23
**Branch:** `phase9-dirac-hydrogen`
**Status:** approved (standing authorization: user said "continue next phase", away during build)
**Parent spec:** `2026-07-04-atom-sim-requirements-design.md` (§3.4 / §9 Phase 3 list: "exact Dirac hydrogen") · **Builds on:** `analytic/hydrogen.py`, `analytic/fine_structure.py`, the Levels view.

---

## 1. Goal and success criteria

The code already names this phase. `fine_structure.py` tags its perturbative α² shift with
`refinement="exact Dirac hydrogen solution (planned Phase 3 flagship)"`. Phase 9 delivers that
refinement: the **closed-form Dirac-Coulomb energy** for a hydrogen-like atom, `EXACT`-tier,
sitting honestly between the perturbative `APPROXIMATION` and reality.

The exact Dirac energy captures fine structure to **all orders in (Zα)**, not just α². Its
signature teaching moment is a degeneracy the perturbative model shares but cannot explain: the
energy depends on **(n, j) only**, so `2s₁/₂` and `2p₁/₂` are **exactly degenerate**. Reality
splits them (the Lamb shift) — which this model deliberately omits. Naming that gap *is* the
honesty lesson.

**Done when:**

1. `analytic/dirac.py` computes the exact Dirac-Coulomb binding energy `E(n, j)` as an `EXACT`
   `Quantity`, with assumptions listing exactly what the Dirac-Coulomb model omits (Lamb/QED,
   hyperfine, finite nuclear size, two-body recoil beyond reduced mass).
2. Validation proves the honesty loop closes: the Dirac energy reduces to Bohr as α→0, agrees
   with `Bohr + perturbative fine structure` to **O(α⁴)** (residual shrinks 16× when α halves),
   matches the published H `1s₁/₂` value, and reproduces the exact `(n,j)`-degeneracy.
3. `/api/levels` gains a `dirac` mode: when set, the fine-level array carries `EXACT` Dirac
   energies (per `(n,l,j)`, driven by `(n,j)`), and the response echoes the model.
4. The Levels view offers, when fine structure is on, an **α² perturbative vs Dirac exact**
   choice; Dirac levels are badged `EXACT`, with the `2s₁/₂ = 2p₁/₂` / Lamb-shift caption.
5. The choice is deep-linkable and round-trip tested.
6. The supercritical regime `Zα ≥ j + ½` (where the point-Coulomb Dirac solution ceases to be
   real — the "diving into the negative continuum") is **rejected**, not silently returned as a
   complex or NaN energy.
7. Suite green in CI: engine analytic validation, server route, web logic + URL round-trip.

## 2. Physics (the exact core)

In Hartree atomic units (ℏ = mₑ = e = 1) the speed of light is `c = 1/α ≈ 137.036`. For a
hydrogen-like atom of nuclear charge `Z` and reduced-mass ratio `μ = μ/mₑ`, the exact eigenvalue
of the one-body Dirac-Coulomb Hamiltonian, **binding energy** (rest energy subtracted), is:

```
γ      = sqrt((j + 1/2)^2 - (Z α)^2)
D      = n - (j + 1/2) + γ                       # = n_r + γ,  n_r >= 0
E_bind = (μ / α^2) * ( [1 + (Z α / D)^2]^(-1/2) - 1 )      [hartree]
```

- Depends on `n` and `j` only — **not `l`**. Different `l` at the same `(n, j)` are exactly
  degenerate. This is the honest heart of the phase.
- `μ / α^2` is the (reduced) rest energy `μ c²`; the bracket minus 1 is the fractional binding.
- Real requires `(j + 1/2)^2 > (Z α)^2`, i.e. `Z α < j + 1/2`. For `j = 1/2` this is `Z < ~137`;
  larger `Z` at `j = 1/2` is supercritical and rejected (success criterion 6).

### 2.1 Fidelity: why `EXACT`, and what it still omits

The Dirac-Coulomb solution is the **exact closed form of its model**, exactly as analytic
Schrödinger hydrogen (`analytic/hydrogen.py`) is `EXACT` for *its* model. So the tier is `EXACT`,
with assumptions naming the physics beyond the model:

- no Lamb shift / QED radiative corrections (this is what really splits `2s₁/₂`–`2p₁/₂`),
- no hyperfine structure, no finite-nuclear-size correction,
- reduced mass enters by `μ`-scaling the rest-energy prefactor; full two-body relativistic
  recoil (Breit / QED) beyond that is neglected. (Same reduced-mass convention the whole engine
  already uses.)

`error_estimate` is **not** a numerical error (the formula is exact); it is the *scale of the
omitted physics*, dominated by the Lamb shift, quantified as roughly `α³ · |E_bohr| · Z-scaling`
so the readout honestly says "reality departs from this by about …". The `refinement` field points
at "QED / Lamb shift", the next rung.

### 2.2 The honesty loop with the perturbative module

Expanding `E_bind` to order `(Zα)²` returns exactly `E_bohr(n) + ΔE_Pauli(n, j)`. So the existing
`APPROXIMATION` is the α²-truncation of this `EXACT` result. The validation asserts the residual
`E_dirac - (E_bohr + ΔE_fs)` is O(α⁴) and shrinks 16× under α→α/2 — turning the two modules into a
checkable pair rather than two unrelated numbers.

## 3. Decisions locked in

| Question | Decision |
|---|---|
| Fidelity | `EXACT` (closed form of the Dirac-Coulomb model), assumptions name the omitted physics. Rejected: `APPROXIMATION` — that would misrepresent an exact eigenvalue; the omissions are *model scope*, not approximation error, and belong in assumptions (mirrors Schrödinger hydrogen). |
| Energy convention | Binding energy (rest energy subtracted), hartree — matches every other level in the app. |
| Reduced mass | `μ`-scale the rest-energy prefactor `μ/α²`; recoil beyond that in assumptions. Consistent with the whole engine. |
| `α` argument | Threaded like `fine_structure_shift`: `EXACT` at real α, `COUNTERFACTUAL` when altered (future What-If use), same seam, no signature churn. |
| Supercritical `Zα ≥ j+½` | Raise `ValueError` with a clear message. Rejected: returning `NaN`/complex (violates the prime directive). |
| Server API | Add `dirac: bool = False` to `/api/levels`; when true the `fine` array is Dirac and the response echoes `dirac=true`. Rejected: a `relativistic` enum replacing `fine_structure` — needless churn to the stable levels/spectrum/state contract. |
| `l` in the response | Dirac `fine` entries still enumerate `(n, l, j)` (so the view lays them out the same way); equal-`(n,j)` rows carry identical energies, making the degeneracy visible rather than asserted. |
| Frontend control | When fine structure is ON, a sub-choice "α² perturbative / Dirac exact". A single `dirac` boolean in the store, gated by `fineStructure`. Keeps `fineStructure` (used by spectrum + state) untouched. |
| Scope | Levels view only. The What-If constants lab (Dirac at altered α) and the spectrum view stay perturbative this phase (YAGNI). |

## 4. Engine — `analytic/dirac.py` (new)

```
dirac_energy(n: int, j: float, Z: int = 1, mu_ratio: float = 1.0, alpha: float = ALPHA) -> Quantity
```

- Validate `n >= 1`; `j` half-integer in `{1/2, 3/2, …, n-1/2}` (reuse the `(n,l,j)` consistency
  already encoded by `validate_quantum_numbers`/`validate_j`, adapted to `(n, j)`); `Z >= 1`;
  and `Z*alpha < j + 0.5` (else `ValueError`, supercritical).
- Compute `E_bind` per §2. Tier: `EXACT` at real α, `COUNTERFACTUAL` when α altered
  (`math.isclose` against `ALPHA`, same test as `fine_structure.py`).
- Assumptions per §2.1; `error_estimate` = the omitted-physics scale (Lamb-dominated,
  `~ (Z*alpha)**3 * abs(E_bohr)`-ish, documented as an order-of-magnitude honesty figure, not a
  bound on the formula); `refinement="QED / Lamb shift (2s-2p splitting), then hyperfine"`.
- Helper `dirac_fine_splitting(n, l, Z, mu_ratio, alpha)` optional convenience returning
  `E(n, j=l+½) - E(n, j=l-½)` for l≥1 (used by a validation test; export only if a test needs it).

Units: hartree internally; eV conversion stays at the server boundary as everywhere else.

## 5. Server — `server/app.py` + `schemas.py`

- `/api/levels` gains `dirac: bool = False`. When `dirac` is true (non-screened systems only),
  build `fine` from `dirac_energy`: for each `(n, l, j)`, `energy = dirac_energy(n, j, …)` and
  `shift = energy - E_bohr(n)` (the total relativistic shift from the Bohr level, `EXACT`). Reuses
  `FineLevelModel` unchanged; the `EXACT` provenance rides through `QuantityModel`.
- The `fine` array is built when `dirac or fine_structure` is true: if `dirac`, each entry uses
  `dirac_energy` (EXACT); otherwise `level_energy` (perturbative), exactly as today. `dirac` takes
  precedence over `fine_structure` for the array contents when both are set.
- `LevelsResponse` gains `dirac: bool = False` (echo). Existing `fine_structure`/`alpha` fields
  keep their meaning and are echoed unchanged.
- Validation: supercritical `dirac_energy` `ValueError` → HTTP 422 with the message. `dirac` is
  inert for screened systems (they return `ScreenedLevelsModel` before this branch).

## 6. Web — `web/src`

- **`state/store.ts`**: add `dirac: boolean` (default false) + `setDirac`. It is part of the
  `INVALIDATED`-style level state only for the Levels view fetch; `loadLevels` passes `dirac`.
  Setting `dirac` clears the cached levels so stale physics never renders.
- **`api/client.ts` + `api/types.ts`**: `getLevels` gains `dirac`; `LevelsResponse` type gains
  `dirac`. `FineLevel` already carries `energy.provenance`, so the badge needs no new field.
- **`components/LevelsView.tsx`**: when `fineStructure` is on, render a two-option control
  "α² perturbative / Dirac (exact)". In Dirac mode: badge the fine column `EXACT` (from
  provenance), and show the caption: "Dirac is exact for a point nucleus: energy depends on n and
  j only, so 2s₁/₂ and 2p₁/₂ coincide. Reality splits them by the Lamb shift, which this model
  omits." Perturbative mode is unchanged.
- **`lib/urlState.ts`**: serialize `dirac` (e.g. `dirac=1`) only when true and `fineStructure` is
  on; parse hard; round-trip tested. Add to `URL_DEFAULTS` and `main.tsx`'s serialized state.

## 7. Honesty / provenance (the heart)

- Dirac energy is `EXACT` — the exact eigenvalue of the Dirac-Coulomb model — with assumptions
  that name every omitted effect, so "exact" is never overread as "reality".
- The `2s₁/₂ = 2p₁/₂` degeneracy is shown, not hidden; the caption attributes the missing real
  splitting to the Lamb shift the model omits. This is the phase's teaching payload.
- The perturbative `APPROXIMATION` and this `EXACT` result are cross-checked in the test suite
  (O(α⁴) residual), so the two fidelity tiers are provably consistent, not merely co-existing.

## 8. Out of scope (YAGNI)

- Dirac spectra in the Spectrum view; Dirac in the What-If constants lab at altered α (engine is
  ready via the α seam, UI deferred).
- Dirac radial wavefunctions / four-spinors and any cloud/plane rendering (energies only).
- Lamb shift, hyperfine, finite nuclear size (named as the next rungs, not built).
- Supercritical / negative-continuum physics beyond a clean rejection.

## 9. Testing (validation, not smoke)

- **Engine (`tests/test_dirac.py`)**:
  - Non-relativistic limit: `dirac_energy(n, j, alpha=1e-4)` ≈ `energy(n)` (Bohr) to tight rtol.
  - O(α⁴) honesty loop: `residual(α) = |dirac_energy(n,j) - (energy(n) + fine_structure_shift(n,l,j))|`
    is tiny, and `residual(α/2)` is ≈ 16× smaller (α⁴ scaling) for a representative `(n,l,j)`.
  - Published value: `dirac_energy(1, 0.5, Z=1).value` ≈ `-0.5000066` hartree (literature) to ~1e-7.
  - Exact degeneracy: `dirac_energy(2, 0.5)` for `l=0` and `l=1` inputs are bit-identical (function
    of `(n,j)` only).
  - Fine-structure interval: `dirac_fine_splitting(2, 1, Z=1)` matches the perturbative 2p₃/₂–2p₁/₂
    splitting to O(α⁴).
  - Supercritical: `dirac_energy(1, 0.5, Z=200)` raises `ValueError`.
- **Server (`tests/test_server.py`)**: `/api/levels?system=h&n_max=3&dirac=true` → 200, `dirac` echoed
  true, a fine level's `energy.provenance.fidelity == "exact"`, and the two `2,·,j=0.5` entries share
  one energy. Supercritical system (high-Z generic) → 422.
- **Web (`*.test.ts`)**: `getLevels` includes `dirac=true` in the URL when set; URL round-trip for
  `fs=1&dirac=1`; the perturbative default omits `dirac`.
