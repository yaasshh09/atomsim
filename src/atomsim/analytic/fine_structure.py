"""Perturbative fine structure: spin-orbit + relativistic KE + Darwin, order alpha^2.

The standard combined Pauli result, a function of n and j only:
    Delta E = -(mu' Z^4 alpha^2 / (2 n^4)) (n/(j+1/2) - 3/4)   [hartree]
APPROXIMATION tier by construction; the error estimate carries the three known
neglected scales (alpha^4 terms, nuclear recoil O(m/M), electron g-2).
"""

from atomsim.analytic.hydrogen import energy, validate_quantum_numbers
from atomsim.constants import ALPHA
from atomsim.provenance import Fidelity, Provenance, Quantity

_G2 = 2.0 * 0.00116  # anomalous-moment scale on the spin-orbit piece

_FS_ASSUMPTIONS = (
    "Pauli approximation, order alpha^2: spin-orbit + relativistic kinetic + Darwin",
    "electron g = 2 exactly (anomalous moment ~0.1% of the splitting neglected)",
    "reduced-mass scaling to leading order; nuclear recoil O(m/M) neglected",
    "no Lamb shift / QED, no hyperfine structure",
)


def validate_j(l: int, j: float) -> None:
    if j < 0.5 or abs(abs(j - l) - 0.5) > 1e-12:
        raise ValueError(f"j must be l +/- 1/2 (and >= 1/2), got l={l}, j={j}")


def fine_structure_shift(
    n: int, l: int, j: float, Z: int = 1, mu_ratio: float = 1.0, m_over_M: float = 0.0
) -> Quantity:
    """Fine-structure energy shift Delta E(n, l, j) in hartree (APPROXIMATION)."""
    validate_quantum_numbers(n, l)
    validate_j(l, j)
    value = -(mu_ratio * Z**4 * ALPHA**2 / (2.0 * n**4)) * (n / (j + 0.5) - 0.75)
    error = abs(value) * ((Z * ALPHA) ** 2 + m_over_M + _G2)
    return Quantity(
        value=value,
        unit="hartree",
        label=f"dE_fs {n},{l},j={j:g} (Z={Z}, mu/m_e={mu_ratio:g})",
        provenance=Provenance(
            fidelity=Fidelity.APPROXIMATION,
            method=(
                "combined Pauli fine structure "
                "dE = -(mu' Z^4 alpha^2 / 2 n^4)(n/(j+1/2) - 3/4)"
            ),
            assumptions=_FS_ASSUMPTIONS,
            error_estimate=error,
            refinement="exact Dirac hydrogen solution (planned Phase 3 flagship)",
        ),
    )


def level_energy(
    n: int, l: int, j: float, Z: int = 1, mu_ratio: float = 1.0, m_over_M: float = 0.0
) -> Quantity:
    """Bohr energy plus fine-structure shift, in hartree (APPROXIMATION)."""
    bohr = energy(n, Z=Z, mu_ratio=mu_ratio)
    shift = fine_structure_shift(n, l, j, Z=Z, mu_ratio=mu_ratio, m_over_M=m_over_M)
    return Quantity(
        value=bohr.value + shift.value,
        unit="hartree",
        label=f"E {n},{l},j={j:g} (Z={Z}, mu/m_e={mu_ratio:g})",
        provenance=Provenance(
            fidelity=Fidelity.APPROXIMATION,
            method=f"{bohr.provenance.method} + {shift.provenance.method}",
            assumptions=_FS_ASSUMPTIONS,
            error_estimate=shift.provenance.error_estimate,
            refinement=shift.provenance.refinement,
        ),
    )
