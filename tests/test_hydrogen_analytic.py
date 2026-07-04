import pytest
from scipy.constants import electron_mass, physical_constants, proton_mass

from atomsim.analytic.hydrogen import energy
from atomsim.constants import HARTREE_EV
from atomsim.provenance import Fidelity


def test_hydrogen_ground_state_is_minus_half_hartree():
    q = energy(1)
    assert q.value == pytest.approx(-0.5, abs=1e-15)
    assert q.unit == "hartree"
    assert q.provenance.fidelity is Fidelity.EXACT


def test_energy_scales_as_z_squared_over_n_squared():
    assert energy(2, Z=3).value == pytest.approx(-0.5 * 9 / 4, rel=1e-14)


def test_helium_plus_ground_state():
    assert energy(1, Z=2).value == pytest.approx(-2.0, rel=1e-14)


def test_positronium_via_reduced_mass():
    # mu = m_e/2 exactly -> binding 6.803 eV
    q = energy(1, mu_ratio=0.5)
    assert q.value == pytest.approx(-0.25, rel=1e-14)
    assert q.value * HARTREE_EV == pytest.approx(-6.803, abs=0.001)


def test_muonic_hydrogen_ground_state_in_ev():
    m_mu = physical_constants["muon mass"][0]
    mu_ratio = (m_mu * proton_mass / (m_mu + proton_mass)) / electron_mass
    e_ev = energy(1, mu_ratio=mu_ratio).value * HARTREE_EV
    assert e_ev == pytest.approx(-2528.5, abs=2.0)  # known ~ -2.53 keV


def test_invalid_quantum_numbers_raise():
    with pytest.raises(ValueError):
        energy(0)
    with pytest.raises(ValueError):
        energy(-3)


def test_provenance_names_its_assumptions():
    p = energy(1).provenance
    joined = " ".join(p.assumptions).lower()
    assert "non-relativistic" in joined
    assert "point nucleus" in joined
