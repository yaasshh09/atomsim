"""Provenance: every physical quantity says how it was computed and how much to trust it.

This is the mechanical enforcement of the project's prime directive:
the model never quietly lies about physics.
"""

from dataclasses import dataclass, field
from enum import Enum


class Fidelity(Enum):
    EXACT = "exact"                    # closed-form solution of the stated model
    NUMERICAL = "numerical"            # converged numerical solution, quantified error
    APPROXIMATION = "approximation"    # honest simplified model, assumptions stated
    COUNTERFACTUAL = "counterfactual"  # deliberately altered physics, computed rigorously
    VISUAL_LIBERTY = "visual_liberty"  # purely presentational choice, disclosed


@dataclass(frozen=True)
class Provenance:
    fidelity: Fidelity
    method: str
    assumptions: tuple[str, ...] = field(default=())
    error_estimate: float | None = None  # same unit as the quantity it describes
    refinement: str | None = None        # what would make this more accurate


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str
    label: str
    provenance: Provenance
