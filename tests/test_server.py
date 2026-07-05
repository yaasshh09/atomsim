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
    assert body["energy"]["value"] == pytest.approx(-0.125)
    assert body["energy"]["unit"] == "hartree"
    assert body["energy"]["provenance"]["fidelity"] == "exact"
    assert body["energy_ev"]["unit"] == "eV"
    assert body["energy_ev"]["value"] == pytest.approx(-3.40, abs=0.01)
    assert body["mean_radius"]["value"] == pytest.approx(5.0)


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
