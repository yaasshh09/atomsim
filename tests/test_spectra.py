import numpy as np
import pytest

from atomsim.provenance import Fidelity
from atomsim.spectra import LineList, SpectralLine, transition_lines
from atomsim.systems import get_system


def _wavelengths(lines):
    return np.array([ln.wavelength.value for ln in lines])


def test_gross_lyman_alpha_wavelength():
    ll = transition_lines(get_system("h"), n_max=3)
    lya = [
        ln for ln in ll.lines
        if (ln.n_upper, ln.n_lower) == (2, 1) and ln.l_upper == 1
    ]
    assert len(lya) == 1
    # mu-corrected gross Lyman-alpha: 121.567 nm vacuum
    assert lya[0].wavelength.value == pytest.approx(121.567, abs=2e-3)
    assert lya[0].wavelength.unit == "nm (vacuum)"
    assert lya[0].energy.value == pytest.approx(10.199, abs=1e-3)


def test_selection_rule_delta_l():
    ll = transition_lines(get_system("h"), n_max=4)
    assert all(abs(ln.l_upper - ln.l_lower) == 1 for ln in ll.lines)
    # 2s -> 1s must be absent
    assert not any(
        (ln.n_upper, ln.l_upper, ln.n_lower) == (2, 0, 1) for ln in ll.lines
    )


def test_gross_lines_are_exact_and_sorted():
    ll = transition_lines(get_system("h"), n_max=5)
    assert isinstance(ll, LineList)
    assert ll.provenance.fidelity is Fidelity.EXACT
    w = _wavelengths(ll.lines)
    assert (np.diff(w) >= 0).all()
    assert all(ln.j_upper is None for ln in ll.lines)


def test_fine_structure_doublet():
    ll = transition_lines(get_system("h"), n_max=2, fine_structure=True)
    lya = [ln for ln in ll.lines if (ln.n_upper, ln.n_lower) == (2, 1)]
    # 2p_{1/2} -> 1s_{1/2} and 2p_{3/2} -> 1s_{1/2}
    assert sorted(ln.j_upper for ln in lya) == [0.5, 1.5]
    dl = abs(lya[0].wavelength.value - lya[1].wavelength.value)
    assert dl == pytest.approx(5.4e-4, rel=0.05)  # Lyman-alpha doublet ~0.54 pm
    assert ll.provenance.fidelity is Fidelity.APPROXIMATION


def test_fine_structure_delta_j_rule():
    ll = transition_lines(get_system("h"), n_max=3, fine_structure=True)
    assert all(abs(ln.j_upper - ln.j_lower) <= 1.0 + 1e-12 for ln in ll.lines)


def test_deuterium_isotope_shift_direction():
    h = transition_lines(get_system("h"), n_max=2).lines[0]
    d = transition_lines(get_system("d"), n_max=2).lines[0]
    assert d.wavelength.value < h.wavelength.value  # heavier nucleus -> bluer
    shift = h.wavelength.value - d.wavelength.value
    assert shift == pytest.approx(0.033, rel=0.05)  # ~33 pm Lyman-alpha H/D shift


def test_positronium_lyman_alpha_is_doubled():
    # lambda ~ 1/mu': lambda(mu'=1) = lambda_H * mu'_H; positronium doubles it
    MU_H = 1836.152673426 / 1837.152673426
    ps = transition_lines(get_system("ps"), n_max=2).lines[0]
    assert ps.wavelength.value == pytest.approx(2.0 * 121.567 * MU_H, rel=1e-4)
    assert ps.wavelength.value == pytest.approx(243.0, abs=0.1)  # literature Ps Lyman-alpha


def test_every_line_carries_provenance():
    ll = transition_lines(get_system("h"), n_max=3, fine_structure=True)
    for ln in ll.lines:
        assert isinstance(ln, SpectralLine)
        assert ln.energy.provenance is not None
        assert ln.wavelength.provenance is not None


def test_n_max_validation():
    with pytest.raises(ValueError):
        transition_lines(get_system("h"), n_max=1)
