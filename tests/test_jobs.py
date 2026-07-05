import pytest

from atomsim.server.jobs import JobStatus, JobStore


def test_create_and_get():
    store = JobStore()
    job = store.create()
    assert job.status is JobStatus.PENDING
    assert store.get(job.id) is job
    assert store.get("nope") is None


def test_run_success_sets_done_result_and_full_progress():
    store = JobStore()
    job = store.create()
    seen: list[float] = []

    def work(progress):
        progress(0.5)
        seen.append(store.get(job.id).progress)
        return "payload"

    store.run(job.id, work)
    assert seen == [0.5]  # progress visible to observers mid-run
    assert job.status is JobStatus.DONE
    assert job.result == "payload"
    assert job.progress == pytest.approx(1.0)


def test_run_failure_sets_error_status_and_message():
    store = JobStore()
    job = store.create()

    def bad(progress):
        raise ValueError("boom")

    store.run(job.id, bad)
    assert job.status is JobStatus.ERROR
    assert "ValueError" in job.error and "boom" in job.error
    assert job.result is None


def test_progress_is_clamped_to_unit_interval():
    store = JobStore()
    job = store.create()

    def work(progress):
        progress(7.0)
        assert job.progress == 1.0
        progress(-3.0)
        assert job.progress == 0.0
        return None

    store.run(job.id, work)


def test_run_unknown_job_raises():
    store = JobStore()
    with pytest.raises(KeyError):
        store.run("nope", lambda progress: None)
