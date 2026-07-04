"""Exact analytic solutions for hydrogen-like (one-electron) atoms.

Hartree atomic units (hbar = m_e = e = 1/(4 pi eps0) = 1). The reduced-mass
ratio mu_ratio = mu/m_e makes isotopes, muonic atoms, and positronium exact
within the same formulas. This module is also the ground truth that validates
the numerical radial solver.
"""

from atomsim.provenance import Fidelity, Provenance, Quantity

_EXACT_ASSUMPTIONS = (
    "non-relativistic Schrodinger equation",
    "point nucleus (no finite-size or QED effects)",
    "nuclear motion included only via reduced-mass ratio",
    "no external fields",
)


def validate_quantum_numbers(n: int, l: int = 0) -> None:  # noqa: E741
    if n < 1:
        raise ValueError(f"principal quantum number n must be >= 1, got {n}")
    if not 0 <= l < n:
        raise ValueError(f"orbital quantum number l must satisfy 0 <= l < n, got l={l}, n={n}")


def energy(n: int, Z: int = 1, mu_ratio: float = 1.0) -> Quantity:
    """Exact bound-state energy E_n = -mu_ratio * Z^2 / (2 n^2), in hartree."""
    validate_quantum_numbers(n)
    value = -mu_ratio * Z**2 / (2.0 * n**2)
    return Quantity(
        value=value,
        unit="hartree",
        label=f"E_{n} (Z={Z}, mu/m_e={mu_ratio:g})",
        provenance=Provenance(
            fidelity=Fidelity.EXACT,
            method="closed-form Bohr formula E_n = -mu' Z^2 / (2 n^2)",
            assumptions=_EXACT_ASSUMPTIONS,
        ),
    )
