import numpy as np
import pytest

from atomsim.analytic.wavefunction import evaluate_state
from atomsim.plane import default_half_extent, plane_grid, screened_plane_grid
from atomsim.provenance import Fidelity


def test_density_matches_direct_evaluation():
    pg = plane_grid(2, 1, 0, quantity="density", resolution=33)
    i, j = 5, 20
    pos = np.array([[pg.axis[j], 0.0, pg.axis[i]]])
    psi = evaluate_state(2, 1, 0, pos).values[0]
    assert pg.values[i, j] == pytest.approx(abs(psi) ** 2, rel=1e-12)


def test_psi_sign_structure_2pz():
    # 2p_z: psi > 0 for z > 0, psi < 0 for z < 0 (rows are z, ascending)
    pg = plane_grid(2, 1, 0, quantity="psi", resolution=33)
    mid = 16  # axis[16] == 0.0 for a 33-point symmetric grid
    assert pg.values[mid + 5, mid] > 0.0
    assert pg.values[mid - 5, mid] < 0.0


def test_density_nonnegative_shape_dtype():
    pg = plane_grid(3, 2, 1, quantity="density", basis="real", resolution=17)
    assert pg.values.shape == (17, 17)
    assert pg.values.dtype == np.float64
    assert (pg.values >= 0.0).all()
    assert pg.basis == "real"


def test_default_extent_and_axis():
    assert default_half_extent(2) == pytest.approx(10.0)
    pg = plane_grid(2, 0, 0, resolution=9)
    assert pg.axis[0] == pytest.approx(-10.0)
    assert pg.axis[-1] == pytest.approx(10.0)
    # mu-scaling shrinks the frame like the orbital itself
    assert default_half_extent(1, Z=1, mu_ratio=100.0) == pytest.approx(0.025)


def test_validation_errors():
    with pytest.raises(ValueError):
        plane_grid(1, 0, 0, quantity="colour")
    with pytest.raises(ValueError):
        plane_grid(1, 0, 0, resolution=1)
    with pytest.raises(ValueError):
        plane_grid(1, 0, 0, half_extent=-1.0)
    with pytest.raises(ValueError):
        plane_grid(1, 1, 0)  # l >= n


def test_provenance_and_units_are_honest():
    dens = plane_grid(1, 0, 0, resolution=8)
    assert dens.provenance.fidelity is Fidelity.EXACT
    assert "y=0" in dens.provenance.method
    assert dens.unit == "bohr^-3"
    psi = plane_grid(1, 0, 0, quantity="psi", resolution=8)
    assert psi.unit == "bohr^-3/2"
    assert any("real" in a for a in psi.provenance.assumptions)


def test_progress_monotone_to_one():
    seen: list[float] = []
    plane_grid(1, 0, 0, resolution=8, progress=seen.append)
    assert seen[-1] == pytest.approx(1.0)
    assert all(b >= a for a, b in zip(seen, seen[1:]))


def test_screened_plane_is_approximation_and_real_signed():
    pg = screened_plane_grid(11, 11, 3, 1, 0, quantity="psi", resolution=64)
    assert pg.provenance.fidelity is Fidelity.APPROXIMATION
    assert pg.values.shape == (64, 64)
    assert np.isrealobj(pg.values)
    assert np.isfinite(pg.values).all()
    assert pg.Z == 11


def test_screened_plane_node_count_along_axis():
    # Na 3s density: 2 radial nodes -> the signed psi along +z axis changes sign twice.
    pg = screened_plane_grid(11, 11, 3, 0, 0, quantity="psi", resolution=401)
    mid = pg.values.shape[1] // 2           # x = 0 column
    col = pg.values[pg.values.shape[0] // 2 :, mid]  # z >= 0 half-ray
    nz = col[np.abs(col) > np.max(np.abs(col)) * 1e-3]
    sign_changes = int(np.sum(np.diff(np.sign(nz)) != 0))
    assert sign_changes == 2


def test_hydrogen_plane_unchanged_exact():
    pg = plane_grid(2, 1, 0, quantity="psi", resolution=32)
    assert pg.provenance.fidelity is Fidelity.EXACT
    assert pg.values.shape == (32, 32)
