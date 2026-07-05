"""Minimal in-memory async-job pattern: create -> run (in any thread) -> poll/stream.

Deliberately simple for a single-user local app; the same pattern later
carries plane-density grids and volumetrics.
"""

import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


@dataclass
class Job:
    id: str
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    result: Any = None
    error: str | None = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self) -> Job:
        job = Job(id=uuid.uuid4().hex)
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def run(self, job_id: str, fn: Callable[[Callable[[float], None]], Any]) -> None:
        """Execute fn in the calling thread, streaming progress into the job."""
        job = self.get(job_id)
        if job is None:
            raise KeyError(f"unknown job id: {job_id}")
        job.status = JobStatus.RUNNING

        def report(fraction: float) -> None:
            job.progress = min(max(fraction, 0.0), 1.0)

        try:
            job.result = fn(report)
        except Exception as exc:  # honest failure: surface type + message
            job.error = f"{type(exc).__name__}: {exc}"
            job.status = JobStatus.ERROR
        else:
            job.progress = 1.0
            job.status = JobStatus.DONE
