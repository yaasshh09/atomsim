"""THE canonical JSON forms of Provenance, Quantity, and Field.

Defined exactly once here; web/src/api/types.ts mirrors these shapes.
Provenance reaches the browser by construction, never as an afterthought.
"""

from typing import Literal

from pydantic import BaseModel

from atomsim.provenance import Field, Provenance, Quantity
from atomsim.spectra import LineComparison, SpectralLine
from atomsim.systems import System

FidelityName = Literal[
    "exact", "numerical", "approximation", "counterfactual", "visual_liberty"
]


class ProvenanceModel(BaseModel):
    fidelity: FidelityName
    method: str
    assumptions: list[str]
    error_estimate: float | None
    refinement: str | None

    @classmethod
    def from_provenance(cls, p: Provenance) -> "ProvenanceModel":
        return cls(
            fidelity=p.fidelity.value,
            method=p.method,
            assumptions=list(p.assumptions),
            error_estimate=p.error_estimate,
            refinement=p.refinement,
        )


class ChannelModel(BaseModel):
    """One binary per-point channel of a sample job (positions / density / phase)."""

    name: str
    dtype: str
    unit: str
    provenance: ProvenanceModel


class QuantityModel(BaseModel):
    value: float
    unit: str
    label: str
    provenance: ProvenanceModel

    @classmethod
    def from_quantity(cls, q: Quantity) -> "QuantityModel":
        return cls(
            value=q.value,
            unit=q.unit,
            label=q.label,
            provenance=ProvenanceModel.from_provenance(q.provenance),
        )


class FieldModel(BaseModel):
    values: list[float]
    grid: list[float]
    unit: str
    grid_unit: str
    label: str
    provenance: ProvenanceModel

    @classmethod
    def from_field(cls, f: Field) -> "FieldModel":
        if f.values.ndim != 1:
            raise ValueError(f"only 1-D fields serialize in M1, got shape {f.values.shape}")
        return cls(
            values=f.values.tolist(),
            grid=f.grid.tolist(),
            unit=f.unit,
            grid_unit=f.grid_unit,
            label=f.label,
            provenance=ProvenanceModel.from_provenance(f.provenance),
        )


class SystemModel(BaseModel):
    key: str
    name: str
    z: int
    mu_ratio: QuantityModel
    m_over_m_nucleus: float
    description: str

    @classmethod
    def from_system(cls, s: System) -> "SystemModel":
        return cls(
            key=s.key,
            name=s.name,
            z=s.Z,
            mu_ratio=QuantityModel.from_quantity(s.mu_ratio),
            m_over_m_nucleus=s.m_over_M,
            description=s.description,
        )


class LineModel(BaseModel):
    n_upper: int
    l_upper: int
    j_upper: float | None
    n_lower: int
    l_lower: int
    j_lower: float | None
    energy_ev: QuantityModel
    wavelength_nm: QuantityModel

    @classmethod
    def from_line(cls, ln: SpectralLine) -> "LineModel":
        return cls(
            n_upper=ln.n_upper, l_upper=ln.l_upper, j_upper=ln.j_upper,
            n_lower=ln.n_lower, l_lower=ln.l_lower, j_lower=ln.j_lower,
            energy_ev=QuantityModel.from_quantity(ln.energy),
            wavelength_nm=QuantityModel.from_quantity(ln.wavelength),
        )


class ComparisonModel(BaseModel):
    wavelength_nm: float
    reference_nm: float
    reference_uncertainty_nm: float | None
    delta_nm: float
    relative_error: float
    within_tolerance: bool

    @classmethod
    def from_comparison(cls, c: LineComparison) -> "ComparisonModel":
        return cls(
            wavelength_nm=c.line.wavelength.value,
            reference_nm=c.reference_nm,
            reference_uncertainty_nm=c.reference_uncertainty_nm,
            delta_nm=c.delta_nm,
            relative_error=c.relative_error,
            within_tolerance=c.within_tolerance,
        )
