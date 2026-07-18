import numpy as np
import pytest

from atomsim.numerics.screening import (
    gsz_parameters,
    screened_potential,
    screening_provenance,
    z_eff,
)
from atomsim.provenance import Fidelity


def test_n1_is_bare_coulomb():
    # With one electron the (N-1) screening term vanishes: V = -Z/r exactly.
    v = screened_potential(z=3, n_electrons=1)
    r = np.array([0.1, 1.0, 5.0])
    assert np.allclose(v(r), -3.0 / r, rtol=0, atol=1e-12)


def test_zeff_limits_neutral_atom():
    # Neutral sodium: Z=N=11. Near r=0 -> Z; far -> Z-N+1 = 1.
    near = z_eff(11, 11, np.array([1e-4]))[0]
    far = z_eff(11, 11, np.array([1e4]))[0]
    assert abs(near - 11.0) < 1e-2
    assert abs(far - 1.0) < 1e-6


def test_potential_is_finite_and_attractive():
    v = screened_potential(11, 11)
    r = np.linspace(0.01, 40.0, 500)
    vals = v(r)
    assert np.isfinite(vals).all()
    assert (vals < 0).all()          # attractive everywhere
    assert vals[0] < vals[-1]        # deeper near the nucleus


def test_parameters_positive():
    d, h = gsz_parameters(11, 11)
    assert d > 0 and h > 0


def test_parameters_only_sourced_for_neutral():
    # We only vendored neutral (N=Z) parameters. An unsourced ion must not
    # silently return an invented value.
    with pytest.raises(ValueError, match="no sourced GSZ"):
        gsz_parameters(11, 9)


def test_provenance_is_approximation():
    prov = screening_provenance(11, 11)
    assert prov.fidelity is Fidelity.APPROXIMATION
    assert "Green" in prov.method or "GSZ" in prov.method
