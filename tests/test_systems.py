import pytest
from scipy import constants as sc

from atomsim.provenance import Fidelity
from atomsim.systems import System, get_system, hydrogen_like, list_systems

R_P = sc.physical_constants["proton-electron mass ratio"][0]
R_MU = sc.physical_constants["muon-electron mass ratio"][0]


def test_registry_contents_and_order():
    keys = [s.key for s in list_systems()]
    assert keys == ["h", "d", "t", "mu-h", "ps", "he+"]


def test_hydrogen_reduced_mass():
    h = get_system("h")
    assert h.Z == 1
    assert h.mu_ratio.value == pytest.approx(R_P / (1.0 + R_P), rel=1e-12)
    assert h.mu_ratio.unit == "m_e"
    assert h.m_over_M == pytest.approx(1.0 / R_P, rel=1e-12)


def test_muonic_hydrogen_is_muon_orbiting_proton():
    muh = get_system("mu-h")
    expected = R_MU * R_P / (R_MU + R_P)  # in m_e units
    assert muh.mu_ratio.value == pytest.approx(expected, rel=1e-9)
    assert muh.mu_ratio.value == pytest.approx(185.84, rel=1e-3)
    assert muh.m_over_M == pytest.approx(R_MU / R_P, rel=1e-9)


def test_positronium_is_exactly_half():
    ps = get_system("ps")
    assert ps.mu_ratio.value == 0.5
    assert ps.m_over_M == 1.0
    assert ps.mu_ratio.provenance.error_estimate in (None, 0.0)


def test_helium_ion():
    he = get_system("he+")
    assert he.Z == 2
    assert he.mu_ratio.value == pytest.approx(7294.3 / 7295.3, rel=1e-4)


def test_provenance_cites_codata():
    d = get_system("d")
    assert d.mu_ratio.provenance.fidelity is Fidelity.EXACT
    assert "CODATA" in d.mu_ratio.provenance.method
    assert d.mu_ratio.provenance.error_estimate is not None  # measured-mass uncertainty


def test_generic_hydrogen_like():
    s = hydrogen_like(3)
    assert isinstance(s, System)
    assert s.Z == 3 and s.mu_ratio.value == 1.0 and s.m_over_M == 0.0
    assert "infinite nuclear mass" in " ".join(s.mu_ratio.provenance.assumptions)
    with pytest.raises(ValueError):
        hydrogen_like(0)


def test_unknown_key_lists_options():
    with pytest.raises(KeyError, match="he\\+"):
        get_system("uranium")
