"""Provenance: every scalar (`Quantity`) or array (`Field`) says how it was computed and trusted.

This is the mechanical enforcement of the project's prime directive:
the model never quietly lies about physics.
"""

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


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


@dataclass(frozen=True)
class Field:
    """Array-valued physical quantity: samples of a function on a 1-D grid.

    Completes the boundary rule: every physical value crossing a module
    boundary is a Quantity (scalar), a Field (array), or a container that
    carries its own Provenance.
    """

    values: np.ndarray
    grid: np.ndarray
    unit: str
    grid_unit: str
    label: str
    provenance: Provenance

    def __post_init__(self) -> None:
        values = np.asarray(self.values)
        grid = np.asarray(self.grid)
        if grid.ndim != 1:
            raise ValueError(f"grid must be 1-D, got shape {grid.shape}")
        if values.shape[-1] != grid.shape[0]:
            raise ValueError(
                f"values last axis ({values.shape[-1]}) must match "
                f"grid length ({grid.shape[0]})"
            )
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "grid", grid)
