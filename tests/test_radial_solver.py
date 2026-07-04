import numpy as np
import pytest

from atomsim.numerics.radial_solver import solve_radial
from atomsim.provenance import Fidelity


def test_3d_harmonic_oscillator_l0_energies():
    # V = r^2/2, mu'=1: exact E = 2k + l + 3/2 -> 1.5, 3.5, 5.5
    sol = solve_radial(lambda r: 0.5 * r**2, l=0, r_max=12.0, n_points=2400, n_states=3)
    got = [q.value for q in sol.energies]
    assert got == pytest.approx([1.5, 3.5, 5.5], abs=1e-4)


def test_3d_harmonic_oscillator_l1_energies():
    sol = solve_radial(lambda r: 0.5 * r**2, l=1, r_max=12.0, n_points=2400, n_states=2)
    got = [q.value for q in sol.energies]
    assert got == pytest.approx([2.5, 4.5], abs=1e-4)


def test_solutions_are_normalized_and_sign_fixed():
    sol = solve_radial(lambda r: 0.5 * r**2, l=0, r_max=12.0, n_points=2400, n_states=3)
    for k in range(3):
        norm = np.trapezoid(sol.u[k] ** 2, sol.r)
        assert norm == pytest.approx(1.0, abs=1e-8)
        first = np.argmax(np.abs(sol.u[k]) > 0.01 * np.abs(sol.u[k]).max())
        assert sol.u[k][first] > 0


def test_state_k_has_k_nodes():
    from atomsim.numerics.analysis import count_sign_changes

    sol = solve_radial(lambda r: 0.5 * r**2, l=0, r_max=12.0, n_points=2400, n_states=4)
    for k in range(4):
        assert count_sign_changes(sol.u[k]) == k


def test_energies_carry_numerical_provenance():
    sol = solve_radial(lambda r: 0.5 * r**2, l=0, r_max=12.0, n_points=1200, n_states=1)
    p = sol.energies[0].provenance
    assert p.fidelity is Fidelity.NUMERICAL
    assert "finite-difference" in p.method
    assert any("grid" in a for a in p.assumptions)
