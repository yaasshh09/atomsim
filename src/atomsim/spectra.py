"""Spectral lines from level differences, with selection rules and provenance.

Gross structure (fine_structure=False): EXACT Bohr levels (mu-scaled); lines
are (n_u, l_u) -> (n_l, l_l) with Delta l = +/-1. With fine structure on:
APPROXIMATION levels from the alpha^2 Pauli shifts, Delta j in {0, +/-1}.
Wavelengths are vacuum, in nm; energies in eV. NIST comparison: see the
compare_lines API (vendored reference data, never live queries).
"""

import itertools
from dataclasses import dataclass

from scipy import constants as _sc

from atomsim.analytic.fine_structure import level_energy
from atomsim.analytic.hydrogen import energy
from atomsim.constants import HARTREE_EV
from atomsim.provenance import Fidelity, Provenance, Quantity
from atomsim.systems import System

_EV_NM = _sc.h * _sc.c / _sc.e * 1e9  # photon wavelength(nm) = _EV_NM / E(eV)


@dataclass(frozen=True)
class SpectralLine:
    n_upper: int
    l_upper: int
    j_upper: float | None
    n_lower: int
    l_lower: int
    j_lower: float | None
    energy: Quantity      # eV
    wavelength: Quantity  # nm, vacuum


@dataclass(frozen=True)
class LineList:
    system_key: str
    n_max: int
    fine_structure: bool
    lines: tuple[SpectralLine, ...]
    provenance: Provenance


def _levels(system: System, n_max: int, fine_structure: bool):
    """Yield (n, l, j, E_hartree Quantity) for all levels up to n_max."""
    for n in range(1, n_max + 1):
        for l in range(n):
            if fine_structure:
                js = [l - 0.5, l + 0.5] if l > 0 else [0.5]
                for j in js:
                    yield n, l, j, level_energy(
                        n, l, j, Z=system.Z,
                        mu_ratio=system.mu_ratio.value, m_over_M=system.m_over_M,
                    )
            else:
                yield n, l, None, energy(n, Z=system.Z, mu_ratio=system.mu_ratio.value)


def transition_lines(
    system: System, n_max: int, fine_structure: bool = False
) -> LineList:
    """All dipole-allowed emission lines among levels with n <= n_max."""
    if n_max < 2:
        raise ValueError(f"n_max must be >= 2 to have any transition, got {n_max}")
    levels = list(_levels(system, n_max, fine_structure))
    lines: list[SpectralLine] = []
    for (nu, lu, ju, eu), (nl, ll_, jl, el) in itertools.permutations(levels, 2):
        if eu.value <= el.value:
            continue
        if abs(lu - ll_) != 1:
            continue
        if fine_structure and abs(ju - jl) > 1.0 + 1e-12:
            continue
        de_ev = (eu.value - el.value) * HARTREE_EV
        tier = Fidelity.APPROXIMATION if fine_structure else Fidelity.EXACT
        prov = Provenance(
            fidelity=tier,
            method=(
                f"level difference: [{eu.provenance.method}] minus "
                f"[{el.provenance.method}]; photon lambda = hc/dE (vacuum)"
            ),
            assumptions=eu.provenance.assumptions
            + ("electric-dipole selection rules (Delta l = +/-1"
               + (", Delta j in {0, +/-1})" if fine_structure else ")"),),
            error_estimate=(
                None if eu.provenance.error_estimate is None
                else (eu.provenance.error_estimate
                      + (el.provenance.error_estimate or 0.0)) * HARTREE_EV
            ),
            refinement=eu.provenance.refinement,
        )
        label = f"{nu}->{nl}"
        lines.append(
            SpectralLine(
                n_upper=nu, l_upper=lu, j_upper=ju,
                n_lower=nl, l_lower=ll_, j_lower=jl,
                energy=Quantity(de_ev, "eV", f"dE {label}", prov),
                wavelength=Quantity(_EV_NM / de_ev, "nm (vacuum)", f"lambda {label}", prov),
            )
        )
    lines.sort(key=lambda ln: ln.wavelength.value)
    return LineList(
        system_key=system.key,
        n_max=n_max,
        fine_structure=fine_structure,
        lines=tuple(lines),
        provenance=Provenance(
            fidelity=Fidelity.APPROXIMATION if fine_structure else Fidelity.EXACT,
            method="dipole-allowed level differences (see per-line provenance)",
            assumptions=("emission lines only (E_upper > E_lower)",
                         "vacuum wavelengths in nm, energies in eV"),
        ),
    )
