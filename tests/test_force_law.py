import math

import numpy as np
import pytest

from atomsim.analytic.hydrogen import energy as hydrogen_energy
from atomsim.numerics.force_law import force_law_levels
from atomsim.provenance import Fidelity
from atomsim.systems import get_system


def test_powerlaw_p1_matches_exact_hydrogen():
    res = force_law_levels("powerlaw", {"p": 1.0}, l=0, system="h", n_states=3)
    assert res.preset_key == "powerlaw"
    assert res.bound_count == 3 and res.requested_count == 3
    mu = get_system("h").mu_ratio.value  # compare like-for-like reduced mass
    for k, level in enumerate(res.counterfactual):
        n = k + 1  # l = 0
        exact = hydrogen_energy(n, Z=1, mu_ratio=mu).value
        assert level.energy.provenance.fidelity is Fidelity.NUMERICAL
        assert math.isclose(level.energy.value, exact, rel_tol=2e-4)


def test_powerlaw_reference_is_exact_hydrogen_ladder():
    res = force_law_levels("powerlaw", {"p": 1.2}, l=1, system="h", n_states=3)
    assert res.reference.kind == "levels"
    assert [item.label for item in res.reference.items] == ["n=2", "n=3", "n=4"]
    assert all(i.energy.provenance.fidelity is Fidelity.EXACT for i in res.reference.items)


def test_powerlaw_degeneracy_breaks_off_p1():
    s = force_law_levels("powerlaw", {"p": 1.2}, l=0, system="h", n_states=2)
    p = force_law_levels("powerlaw", {"p": 1.2}, l=1, system="h", n_states=1)
    e_2s = s.counterfactual[1].energy.value  # (l=0, k=1) -> n=2
    e_2p = p.counterfactual[0].energy.value  # (l=1, k=0) -> n=2
    assert abs(e_2s - e_2p) > 1e-4
    assert e_2s < e_2p  # p > 1 (harder): s below p (alkali ordering)


def test_powerlaw_out_of_range_p_raises():
    with pytest.raises(ValueError, match="p"):
        force_law_levels("powerlaw", {"p": 1.9}, l=0)


def test_potential_curve_is_field_in_hartree():
    res = force_law_levels("powerlaw", {"p": 1.0}, l=0, system="h", n_states=2)
    curve = res.potential_curve
    assert curve.values.shape == curve.grid.shape
    assert curve.unit == "hartree" and curve.grid_unit == "bohr"
    assert curve.provenance.fidelity is Fidelity.EXACT
    assert np.all(curve.grid > 0)


def test_unknown_preset_raises():
    with pytest.raises(ValueError, match="unknown preset"):
        force_law_levels("nope", {}, l=0)
