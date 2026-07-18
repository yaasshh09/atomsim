import math

import pytest

from atomsim.atoms import aufbau_configuration, parse_config
from atomsim.provenance import Fidelity
from atomsim.screened_atom import (
    screened_radial,
    solve_screened_atom,
    valence_ionization_energy,
)

# NIST first ionization energies (eV), for the tier-defining tolerance test.
# Source: NIST ASD ionization energies (public). Retrieved 2026-07-18.
_NIST_IE_EV = {"he": 24.587, "li": 5.392, "na": 5.139}
HARTREE_EV = 27.211386245988


def test_n1_recovers_hydrogenic():
    # One electron in the screened field == bare Coulomb == -Z^2 / 2n^2.
    res = solve_screened_atom(z=3, n_electrons=1, config=parse_config("1s1"))
    e1s = res.orbitals[0].energy.value
    assert math.isclose(e1s, -(3**2) / 2.0, rel_tol=2e-4)
    assert res.orbitals[0].energy.provenance.fidelity is Fidelity.APPROXIMATION


def test_orbital_energy_carries_numerical_subscale():
    res = solve_screened_atom(z=11, n_electrons=11, config=aufbau_configuration(11))
    assert res.orbitals[0].energy.provenance.error_estimate is not None


def test_total_energy_is_occupancy_weighted_sum():
    res = solve_screened_atom(z=6, n_electrons=6, config=aufbau_configuration(6))
    expect = sum(o.occupancy * o.energy.value for o in res.orbitals)
    assert math.isclose(res.total_energy.value, expect, rel_tol=1e-12)


def test_s_below_p_for_same_n():
    # Screening lifts the Coulomb degeneracy: 2s below 2p in carbon.
    res = solve_screened_atom(z=6, n_electrons=6, config=aufbau_configuration(6))
    e = {(o.n, o.l): o.energy.value for o in res.orbitals}
    assert e[(2, 0)] < e[(2, 1)]


@pytest.mark.parametrize("key,z,n", [("he", 2, 2), ("li", 3, 3), ("na", 11, 11)])
def test_valence_ionization_matches_nist(key, z, n):
    res = solve_screened_atom(z=z, n_electrons=n, config=aufbau_configuration(n))
    ie_ev = valence_ionization_energy(res).value * HARTREE_EV
    ref = _NIST_IE_EV[key]
    assert abs(ie_ev - ref) / ref < 0.12  # GSZ valence energies: ~10% class


def test_screened_radial_shapes():
    r_field, p_field = screened_radial(z=11, n_electrons=11, n=3, l=0, points=300)
    assert r_field.values.shape == r_field.grid.shape == (300,)
    assert p_field.unit == "bohr^-1" and r_field.provenance.fidelity is Fidelity.APPROXIMATION
