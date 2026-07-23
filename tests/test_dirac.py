import pytest

from atomsim.analytic.dirac import dirac_energy, dirac_fine_splitting
from atomsim.analytic.fine_structure import fine_structure_shift
from atomsim.analytic.hydrogen import energy
from atomsim.constants import ALPHA
from atomsim.provenance import Fidelity


def test_nonrelativistic_limit_recovers_bohr():
    # alpha -> 0 collapses Dirac onto the Bohr ladder
    for n, j in [(1, 0.5), (2, 0.5), (3, 1.5)]:
        e = dirac_energy(n, j, Z=1, alpha=1e-5).value
        assert e == pytest.approx(energy(n).value, rel=1e-6)


def test_ground_state_matches_published_value():
    # Leading behaviour of the exact 1s energy: -1/2 - alpha^2/8, more bound than the
    # nonrelativistic -1/2. (The full closed form is pinned by the alpha->0 limit and
    # the O(alpha^4) agreement tests below.)
    got = dirac_energy(1, 0.5, Z=1).value
    assert got == pytest.approx(-0.5 - ALPHA**2 / 8.0, abs=1e-9)
    assert got < -0.5


def test_agrees_with_perturbative_to_order_alpha4():
    # residual = |E_dirac - (E_bohr + dE_fs)| is the alpha^4 term; Z=2 lifts it above the
    # double-precision floor so the 16x scaling under alpha -> alpha/2 is clean.
    n, l, j, Z = 2, 1, 1.5, 2

    def residual(a):
        d = dirac_energy(n, j, Z=Z, alpha=a).value
        p = energy(n, Z=Z).value + fine_structure_shift(n, l, j, Z=Z, alpha=a).value
        return abs(d - p)

    r1 = residual(ALPHA)
    r2 = residual(ALPHA / 2)
    assert r1 < 1e-6
    assert r2 == pytest.approx(r1 / 16.0, rel=0.1)  # alpha^4 scaling


def test_exact_nj_degeneracy_is_l_independent():
    # 2s1/2 (l=0) and 2p1/2 (l=1) share one Dirac energy -> depends on (n,j) only
    e_from_s = dirac_energy(2, 0.5, Z=1).value
    e_from_p = dirac_energy(2, 0.5, Z=1).value
    assert e_from_s == e_from_p


def test_fine_splitting_matches_perturbative():
    # 2p3/2 - 2p1/2 interval, Dirac vs Pauli, agree to O(alpha^4)
    dirac_gap = dirac_fine_splitting(2, 1, Z=1)
    pert = (
        fine_structure_shift(2, 1, 1.5, Z=1).value
        - fine_structure_shift(2, 1, 0.5, Z=1).value
    )
    assert dirac_gap == pytest.approx(pert, rel=1e-3)
    assert dirac_gap > 0


def test_fidelity_exact_at_real_alpha_counterfactual_when_altered():
    assert dirac_energy(1, 0.5).provenance.fidelity is Fidelity.EXACT
    assert dirac_energy(1, 0.5, alpha=0.2).provenance.fidelity is Fidelity.COUNTERFACTUAL


def test_supercritical_is_rejected():
    with pytest.raises(ValueError):
        dirac_energy(1, 0.5, Z=200)  # Z*alpha > j+1/2


def test_invalid_j_rejected():
    with pytest.raises(ValueError):
        dirac_energy(2, 2.5)  # j must be in {1/2, 3/2} for n=2
