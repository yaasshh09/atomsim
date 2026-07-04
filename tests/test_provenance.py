import dataclasses

import pytest

from atomsim.provenance import Fidelity, Provenance, Quantity


def test_fidelity_has_exactly_the_five_spec_tiers():
    assert {f.value for f in Fidelity} == {
        "exact",
        "numerical",
        "approximation",
        "counterfactual",
        "visual_liberty",
    }


def test_quantity_carries_full_provenance():
    p = Provenance(
        fidelity=Fidelity.EXACT,
        method="closed-form Bohr formula",
        assumptions=("non-relativistic", "point nucleus"),
    )
    q = Quantity(value=-0.5, unit="hartree", label="E_1", provenance=p)
    assert q.value == -0.5
    assert q.unit == "hartree"
    assert q.provenance.fidelity is Fidelity.EXACT
    assert "point nucleus" in q.provenance.assumptions
    assert q.provenance.error_estimate is None


def test_provenance_and_quantity_are_immutable():
    p = Provenance(fidelity=Fidelity.NUMERICAL, method="fd")
    q = Quantity(value=1.0, unit="bohr", label="r", provenance=p)
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.method = "changed"
    with pytest.raises(dataclasses.FrozenInstanceError):
        q.value = 2.0
