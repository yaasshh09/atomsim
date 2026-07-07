"""Exotic-but-real hydrogen-like system presets (spec 5.5).

Each preset supplies nuclear charge Z and the exact reduced-mass ratio
mu/m_e as a Quantity whose provenance cites the CODATA mass ratios it was
built from. m_over_M (orbiting mass / nuclear mass) feeds the fine-structure
recoil error scale — honesty for positronium comes from a quantified error,
never a silent wrong number.
"""

from dataclasses import dataclass

from scipy import constants as _sc

from atomsim.provenance import Fidelity, Provenance, Quantity


@dataclass(frozen=True)
class System:
    key: str
    name: str
    Z: int
    mu_ratio: Quantity  # mu / m_e, unit "m_e"
    m_over_M: float     # orbiting mass / nuclear mass (recoil scale)
    description: str
    # rms charge radius of the nucleus, in bohr (engine canonical unit).
    # None means honestly absent: a point lepton (positronium's positron) or
    # a generic Z with no identified nucleus — never a silent zero.
    nuclear_radius: Quantity | None = None


def _mass_ratio(constant_name: str) -> tuple[float, float]:
    value, _unit, unc = _sc.physical_constants[constant_name]
    return value, unc


_A0_M = _sc.physical_constants["Bohr radius"][0]


def _radius_quantity(
    r_m: float, unc_m: float, nucleus: str, source: str
) -> Quantity:
    """Nuclear rms charge radius as an engine Quantity (bohr)."""
    return Quantity(
        value=r_m / _A0_M,
        unit="bohr",
        label=f"nuclear rms charge radius ({nucleus})",
        provenance=Provenance(
            fidelity=Fidelity.EXACT,
            method=f"measured rms charge radius of the {nucleus}, {source}",
            assumptions=(
                "reference measurement, not a prediction of this model",
                "the Coulomb engine still treats the nucleus as a point charge",
            ),
            error_estimate=unc_m / _A0_M,
        ),
    )


def _codata_radius(constant_name: str, nucleus: str) -> Quantity:
    r_m, _unit, unc_m = _sc.physical_constants[constant_name]
    return _radius_quantity(
        r_m, unc_m, nucleus, f"CODATA (scipy.constants: {constant_name})"
    )


# Triton is absent from scipy's CODATA table; standard compilation value.
_TRITON_RADIUS = _radius_quantity(
    1.7591e-15, 0.0363e-15, "triton",
    "Angeli & Marinova (2013), At. Data Nucl. Data Tables 99, 69",
)


def _codata_system(
    key: str, name: str, Z: int, nucleus_constant: str, description: str,
    orbiter_constant: str | None = None,
    nuclear_radius: Quantity | None = None,
) -> System:
    """Build a preset from CODATA mass ratios (electron orbiter unless given)."""
    R_nuc, u_nuc = _mass_ratio(nucleus_constant)  # M / m_e
    if orbiter_constant is None:
        r_orb, u_orb, orb_name = 1.0, 0.0, "electron"
    else:
        r_orb, u_orb = _mass_ratio(orbiter_constant)
        orb_name = orbiter_constant.split("-")[0]
    mu = r_orb * R_nuc / (r_orb + R_nuc)
    rel_unc = (u_nuc / R_nuc if R_nuc else 0.0) + (u_orb / r_orb if r_orb else 0.0)
    return System(
        key=key,
        name=name,
        Z=Z,
        mu_ratio=Quantity(
            value=mu,
            unit="m_e",
            label=f"mu/m_e ({name})",
            provenance=Provenance(
                fidelity=Fidelity.EXACT,
                method=(
                    "mu/m_e = m_orb M / (m_orb + M) from CODATA mass ratios "
                    f"(scipy.constants: {nucleus_constant}"
                    + (f", {orbiter_constant})" if orbiter_constant else ")")
                ),
                assumptions=(f"orbiting particle: {orb_name}",),
                error_estimate=mu * rel_unc,
            ),
        ),
        m_over_M=r_orb / R_nuc,
        description=description,
        nuclear_radius=nuclear_radius,
    )


_POSITRONIUM = System(
    key="ps",
    name="Positronium",
    Z=1,
    mu_ratio=Quantity(
        value=0.5,
        unit="m_e",
        label="mu/m_e (Positronium)",
        provenance=Provenance(
            fidelity=Fidelity.EXACT,
            method="mu = m_e/2 exactly (electron-positron, equal masses)",
            assumptions=("orbiting particle: electron; 'nucleus': positron",),
            error_estimate=0.0,
        ),
    ),
    m_over_M=1.0,
    description="Electron bound to a positron; recoil is O(1), fine structure "
    "unreliable at alpha^2 (error estimate says so).",
)

_SYSTEMS: tuple[System, ...] = (
    _codata_system("h", "Hydrogen", 1, "proton-electron mass ratio",
                   "Ordinary hydrogen: electron + proton.",
                   nuclear_radius=_codata_radius("proton rms charge radius", "proton")),
    _codata_system("d", "Deuterium", 1, "deuteron-electron mass ratio",
                   "Heavy hydrogen: electron + deuteron.",
                   nuclear_radius=_codata_radius("deuteron rms charge radius", "deuteron")),
    _codata_system("t", "Tritium", 1, "triton-electron mass ratio",
                   "Radioactive hydrogen isotope: electron + triton.",
                   nuclear_radius=_TRITON_RADIUS),
    _codata_system("mu-h", "Muonic hydrogen", 1, "proton-electron mass ratio",
                   "Muon orbiting a proton: ~186x smaller, ~186x deeper.",
                   orbiter_constant="muon-electron mass ratio",
                   nuclear_radius=_codata_radius("proton rms charge radius", "proton")),
    _POSITRONIUM,
    _codata_system("he+", "Helium ion He+", 2, "alpha particle-electron mass ratio",
                   "One-electron helium: Z=2 scaling on real helium-4.",
                   nuclear_radius=_codata_radius(
                       "alpha particle rms charge radius", "alpha particle")),
)


def list_systems() -> tuple[System, ...]:
    return _SYSTEMS


def get_system(key: str) -> System:
    for s in _SYSTEMS:
        if s.key == key:
            return s
    raise KeyError(f"unknown system {key!r}; available: {[s.key for s in _SYSTEMS]}")


def hydrogen_like(Z: int, mu_ratio: float = 1.0) -> System:
    """Generic one-electron ion with charge Z (infinite nuclear mass by default)."""
    if Z < 1:
        raise ValueError(f"Z must be >= 1, got {Z}")
    assumptions = (
        ("infinite nuclear mass (mu_ratio = 1)",) if mu_ratio == 1.0
        else (f"user-supplied mu_ratio = {mu_ratio:g}",)
    )
    return System(
        key=f"z{Z}",
        name=f"Hydrogen-like Z={Z}",
        Z=Z,
        mu_ratio=Quantity(
            value=mu_ratio,
            unit="m_e",
            label=f"mu/m_e (Z={Z})",
            provenance=Provenance(
                fidelity=Fidelity.EXACT,
                method="user-specified reduced-mass ratio",
                assumptions=assumptions,
            ),
        ),
        m_over_M=0.0,
        description=f"Generic one-electron ion, Z={Z}.",
    )
