import time

import numpy as np
import pytest
from fastapi.testclient import TestClient

import atomsim
from atomsim.server.app import create_app
from atomsim.server.jobs import JobStatus


@pytest.fixture()
def client():
    with TestClient(create_app()) as c:
        yield c


def _wait_done(client, job_id, deadline_s=30.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < deadline_s:
        body = client.get(f"/api/jobs/{job_id}").json()
        if body["status"] in ("done", "error"):
            return body
        time.sleep(0.05)
    raise TimeoutError(f"job {job_id} did not finish")


def test_health_reports_version(client):
    body = client.get("/api/health").json()
    assert body == {"status": "ok", "version": atomsim.__version__}


def test_state_carries_exact_provenance(client):
    r = client.get("/api/state/2/1/0")
    assert r.status_code == 200
    body = r.json()
    # mu-aware since M2: the M1 endpoint silently assumed infinite nuclear mass
    assert body["energy"]["value"] == pytest.approx(-0.125 * 0.9994557, rel=1e-6)
    assert body["energy"]["unit"] == "hartree"
    assert body["energy"]["provenance"]["fidelity"] == "exact"
    assert body["energy_ev"]["unit"] == "eV"
    assert body["energy_ev"]["value"] == pytest.approx(-3.40, abs=0.01)
    assert body["mean_radius"]["value"] == pytest.approx(5.0 / 0.9994557, rel=1e-6)


def test_state_rejects_invalid_quantum_numbers(client):
    assert client.get("/api/state/1/1/0").status_code == 422   # l == n
    assert client.get("/api/state/2/1/2").status_code == 422   # |m| > l
    assert client.get("/api/state/0/0/0").status_code == 422   # n < 1


def test_sample_job_end_to_end(client):
    r = client.post(
        "/api/jobs/sample", json={"n": 1, "l": 0, "m": 0, "count": 5000, "seed": 7}
    )
    assert r.status_code == 200
    job_id = r.json()["id"]

    final = _wait_done(client, job_id)
    assert final["status"] == "done"
    assert final["progress"] == pytest.approx(1.0)

    meta = client.get(f"/api/jobs/{job_id}/meta").json()
    assert meta["count"] == 5000
    assert meta["dtype"] == "float32"
    assert meta["layout"] == "xyz-interleaved"
    assert meta["unit"] == "bohr"
    assert meta["provenance"]["fidelity"] == "numerical"

    raw = client.get(f"/api/jobs/{job_id}/data")
    assert raw.headers["content-type"].startswith("application/octet-stream")
    positions = np.frombuffer(raw.content, dtype=np.float32).reshape(-1, 3)
    assert positions.shape == (5000, 3)
    assert np.isfinite(positions).all()


def test_sample_rejects_invalid_body(client):
    assert (
        client.post("/api/jobs/sample", json={"n": 1, "l": 1, "m": 0}).status_code == 422
    )
    assert (
        client.post(
            "/api/jobs/sample", json={"n": 1, "l": 0, "m": 0, "count": 10}
        ).status_code
        == 422
    )  # below pydantic ge=1000


def test_unknown_job_is_404(client):
    assert client.get("/api/jobs/deadbeef").status_code == 404
    assert client.get("/api/jobs/deadbeef/meta").status_code == 404
    assert client.get("/api/jobs/deadbeef/data").status_code == 404


def test_meta_before_done_is_409(client):
    job = client.app.state.jobs.create()  # created but never run
    assert client.get(f"/api/jobs/{job.id}/meta").status_code == 409
    assert client.get(f"/api/jobs/{job.id}/data").status_code == 409


def test_websocket_streams_progress_to_done(client):
    r = client.post(
        "/api/jobs/sample", json={"n": 2, "l": 1, "m": 0, "count": 20000, "seed": 1}
    )
    job_id = r.json()["id"]
    messages = []
    with client.websocket_connect(f"/ws/jobs/{job_id}") as ws:
        for _ in range(600):
            msg = ws.receive_json()
            messages.append(msg)
            if msg["status"] in ("done", "error"):
                break
    assert messages[-1]["status"] == "done"
    assert messages[-1]["progress"] == pytest.approx(1.0)


def test_job_error_surfaces_via_status(client):
    jobs = client.app.state.jobs
    job = jobs.create()

    def bad(progress):
        raise RuntimeError("sampler exploded")

    jobs.run(job.id, bad)
    body = client.get(f"/api/jobs/{job.id}").json()
    assert body["status"] == "error"
    assert "sampler exploded" in body["error"]
    assert body["status"] == JobStatus.ERROR.value


def test_systems_endpoint_lists_presets(client):
    body = client.get("/api/systems").json()
    keys = [s["key"] for s in body["systems"]]
    assert keys == ["h", "d", "t", "mu-h", "ps", "he+"]
    mu = body["systems"][0]["mu_ratio"]
    assert mu["provenance"]["fidelity"] == "exact"
    assert "CODATA" in mu["provenance"]["method"]


def test_state_accepts_system_and_fine_structure(client):
    body = client.get("/api/state/2/1/0?system=he%2B&fine_structure=true").json()
    assert body["system"]["key"] == "he+"
    assert body["energy"]["value"] == pytest.approx(-0.5 * 0.999863, rel=1e-4)
    js = sorted(lvl["j"] for lvl in body["levels"])
    assert js == [0.5, 1.5]
    assert body["levels"][0]["shift"]["provenance"]["fidelity"] == "approximation"


def test_state_defaults_stay_hydrogen_gross(client):
    body = client.get("/api/state/2/1/0").json()
    assert body["system"]["key"] == "h"
    assert body["levels"] == []
    # mu-scaled now: -0.125 * mu'
    assert body["energy"]["value"] == pytest.approx(-0.125 * 0.9994557, rel=1e-6)


def test_state_unknown_system_is_422(client):
    assert client.get("/api/state/1/0/0?system=xenon").status_code == 422


def test_radial_endpoint_fields(client):
    body = client.get("/api/radial/2/1?points=200").json()
    rw, rp = body["r_wavefunction"], body["radial_probability"]
    assert len(rw["grid"]) == 200 and len(rw["values"]) == 200
    assert rw["provenance"]["fidelity"] == "exact"
    p = np.array(rp["values"])
    g = np.array(rp["grid"])
    assert np.trapezoid(p, g) == pytest.approx(1.0, abs=5e-3)  # P(r) normalized


def test_spectrum_endpoint_with_comparison(client):
    body = client.get("/api/spectrum?system=h&n_max=6").json()
    assert body["reference_citation"] and "NIST" in body["reference_citation"]
    assert len(body["lines"]) > 10
    assert body["comparison"] is not None
    assert all(c["within_tolerance"] for c in body["comparison"])


def test_spectrum_without_reference_data(client):
    body = client.get("/api/spectrum?system=ps&n_max=3").json()
    assert body["comparison"] is None
    assert body["reference_citation"] is None
    assert len(body["lines"]) > 0


def test_sample_job_real_basis_and_system(client):
    r = client.post(
        "/api/jobs/sample",
        json={"n": 2, "l": 1, "m": 1, "count": 5000, "seed": 3,
              "basis": "real", "system": "d"},
    )
    job_id = r.json()["id"]
    final = _wait_done(client, job_id)
    assert final["status"] == "done"
    meta = client.get(f"/api/jobs/{job_id}/meta").json()
    assert meta["basis"] == "real"
    assert meta["system"] == "d"


def test_sample_job_rejects_bad_basis(client):
    r = client.post(
        "/api/jobs/sample",
        json={"n": 1, "l": 0, "m": 0, "basis": "cartoon"},
    )
    assert r.status_code == 422
