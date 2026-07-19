"""Solve a screened multi-electron atom in the GSZ central field (APPROXIMATION).

Each angular momentum l is solved once in V_eff(r); radial state k is principal
number n = k + l + 1. The configuration decides occupancy and thus the summed
energy -- the field itself depends only on (Z, N). Orbital energies are
APPROXIMATION (model error dominates) carrying the numerical solve error as a
quantified sub-scale. See docs/superpowers/specs/
2026-07-18-phase6-screened-atoms-design.md.
"""

import dataclasses
from dataclasses import dataclass

import numpy as np

from atomsim.analytic.angular import spherical_harmonic
from atomsim.analytic.wavefunction import WavefunctionValues
from atomsim.atoms import Configuration, is_ground
from atomsim.numerics.radial_solver import solve_radial_with_error
from atomsim.numerics.screening import screened_potential, screening_provenance
from atomsim.provenance import Fidelity, Field, Provenance, Quantity

_SCREENED_EVAL_POINTS = 4096


@dataclass(frozen=True)
class Orbital:
    n: int
    l: int
    occupancy: int
    energy: Quantity  # APPROXIMATION, hartree


@dataclass(frozen=True)
class ScreenedAtomResult:
    key: str
    z: int
    n_electrons: int
    config: Configuration
    is_ground: bool
    orbitals: tuple[Orbital, ...]
    total_energy: Quantity
    provenance: Provenance


def _r_max(z: int, n_electrons: int, n_top: int) -> float:
    # Orbital extent scales as n^2 / Z_net, where Z_net = Z - N + 1 is the charge
    # the outermost electron feels asymptotically. Neutral atoms (Z_net = 1) keep
    # the 40*(n+1)^2 box; more highly charged ions get a proportionally tighter
    # box, so the compact orbitals stay well resolved on the uniform grid.
    z_net = z - n_electrons + 1
    return 40.0 * (n_top + 1) ** 2 / z_net


def _solve_energies(z: int, n_electrons: int, l: int, n_states: int) -> tuple[Quantity, ...]:
    potential = screened_potential(z, n_electrons)
    r_max = _r_max(z, n_electrons, n_states + l)
    sol = solve_radial_with_error(
        potential, l=l, mu_ratio=1.0, r_max=r_max, n_states=n_states
    )
    prov_model = screening_provenance(z, n_electrons)
    out = []
    for e in sol.energies:
        merged = Provenance(
            fidelity=Fidelity.APPROXIMATION,
            method=f"{prov_model.method}; radial Schrodinger solved numerically",
            assumptions=prov_model.assumptions + e.provenance.assumptions,
            error_estimate=e.provenance.error_estimate,  # numerical sub-scale
            refinement=prov_model.refinement,
        )
        out.append(dataclasses.replace(e, provenance=merged))
    return tuple(out)


def solve_screened_atom(
    z: int, n_electrons: int, config: Configuration,
    l_max: int = 2, n_states_per_l: int = 4,
) -> ScreenedAtomResult:
    occ = {nl: c for nl, c in config}
    l_top = max((l for (_, l), _ in config), default=0)
    n_top = max((n for (n, _), _ in config), default=1)
    l_max = max(l_max, l_top)
    n_states = max(n_states_per_l, n_top)  # enough radial states to reach n_top

    orbitals: list[Orbital] = []
    for l in range(l_max + 1):
        energies = _solve_energies(z, n_electrons, l, n_states)
        for k, e in enumerate(energies):
            n = k + l + 1
            orbitals.append(Orbital(n=n, l=l, occupancy=occ.get((n, l), 0), energy=e))
    orbitals.sort(key=lambda o: (o.energy.value, o.n, o.l))

    total = sum(o.occupancy * o.energy.value for o in orbitals)
    total_prov = Provenance(
        fidelity=Fidelity.APPROXIMATION,
        method="sum of occupancy-weighted independent-particle orbital energies",
        assumptions=(
            "not a variational total energy; ignores e-e double counting",
            f"configuration {'ground' if is_ground(config) else 'non-ground'}",
        ),
    )
    return ScreenedAtomResult(
        key=f"z{z}n{n_electrons}",
        z=z, n_electrons=n_electrons, config=config, is_ground=is_ground(config),
        orbitals=tuple(orbitals),
        total_energy=Quantity(total, "hartree", "E_total", total_prov),
        provenance=screening_provenance(z, n_electrons),
    )


def valence_ionization_energy(result: ScreenedAtomResult) -> Quantity:
    occupied = [o for o in result.orbitals if o.occupancy > 0]
    if not occupied:
        raise ValueError("no occupied orbitals")
    valence = max(occupied, key=lambda o: o.energy.value)
    prov = dataclasses.replace(
        valence.energy.provenance,
        method=valence.energy.provenance.method + "; ionization energy = -epsilon_valence",
    )
    return Quantity(-valence.energy.value, "hartree", "IE_valence", prov)


def screened_radial(
    z: int, n_electrons: int, n: int, l: int, points: int = 400,
) -> tuple[Field, Field]:
    if n <= l:
        raise ValueError(f"n must be > l, got n={n}, l={l}")
    k = n - l - 1
    potential = screened_potential(z, n_electrons)
    r_max = _r_max(z, n_electrons, n)
    sol = solve_radial_with_error(
        potential, l=l, mu_ratio=1.0, r_max=r_max, n_states=k + 1
    )
    r_solver = sol.r
    R = sol.u[k] / r_solver  # R = u / r
    grid = np.linspace(r_solver[0], r_solver[-1], points)
    R_i = np.interp(grid, r_solver, R)
    prov = Provenance(
        fidelity=Fidelity.APPROXIMATION,
        method=f"{screening_provenance(z, n_electrons).method}; numerical R_nl = u/r",
        assumptions=screening_provenance(z, n_electrons).assumptions,
        error_estimate=sol.energies[k].provenance.error_estimate,
    )
    r_field = Field(values=R_i, grid=grid, unit="bohr^-3/2", grid_unit="bohr",
                    label=f"R_{n},{l}(r)", provenance=prov)
    p_field = Field(values=grid**2 * R_i**2, grid=grid, unit="bohr^-1",
                    grid_unit="bohr", label=f"P_{n},{l}(r) = r^2 R^2", provenance=prov)
    return r_field, p_field


def evaluate_screened_state(
    z: int,
    n_electrons: int,
    n: int,
    l: int,
    m: int,
    positions: np.ndarray,
    *,
    basis: str = "complex",
) -> WavefunctionValues:
    """psi_nlm = numerical screened R_nl(|r|) x hydrogenic Y_lm, at (N, 3) positions."""
    pos = np.asarray(positions, dtype=float)
    if pos.ndim != 2 or pos.shape[1] != 3:
        raise ValueError(f"positions must have shape (N, 3), got {pos.shape}")

    r = np.linalg.norm(pos, axis=1)
    safe_r = np.where(r > 0.0, r, 1.0)
    theta = np.arccos(np.clip(pos[:, 2] / safe_r, -1.0, 1.0))
    theta = np.where(r > 0.0, theta, 0.0)
    phi = np.arctan2(pos[:, 1], pos[:, 0])

    r_field, _ = screened_radial(z, n_electrons, n, l, points=_SCREENED_EVAL_POINTS)
    R = np.interp(r, r_field.grid, r_field.values, left=r_field.values[0], right=0.0)
    angular = spherical_harmonic(l, m, theta, phi, basis=basis)
    values = R * angular.values

    base = screening_provenance(z, n_electrons)
    prov = Provenance(
        fidelity=Fidelity.APPROXIMATION,
        method=(
            f"psi_nlm = numerical screened R_nl (u/r) x {angular.provenance.method}; "
            f"{base.method}"
        ),
        assumptions=base.assumptions
        + angular.provenance.assumptions
        + ("values in bohr^-3/2 at Cartesian positions in bohr",),
        error_estimate=r_field.provenance.error_estimate,
    )
    return WavefunctionValues(
        values=values, positions=pos, n=n, l=l, m=m, Z=z, mu_ratio=1.0,
        basis=basis, provenance=prov,
    )
