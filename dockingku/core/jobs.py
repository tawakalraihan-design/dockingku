"""Menjalankan pekerjaan berat (docking, P2Rank) di latar belakang dengan progres."""
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field


@dataclass
class Job:
    id: str
    title: str
    status: str = "queued"  # queued, running, done, failed
    progress: float = 0.0
    message: str = ""
    result: object = None
    log: list[str] = field(default_factory=list)

    def report(self, progress: float, message: str = ""):
        self.progress, self.message = progress, message
        if message:
            self.log.append(message)


class JobRunner:
    def __init__(self, workers: int = 2):
        self.pool = ThreadPoolExecutor(max_workers=workers)
        self.jobs: dict[str, Job] = {}

    def submit(self, title: str, fn, *args, **kwargs) -> Job:
        job = Job(id=uuid.uuid4().hex[:8], title=title)
        self.jobs[job.id] = job

        def run():
            job.status = "running"
            try:
                job.result = fn(*args, job=job, **kwargs)
                job.status, job.progress = "done", 1.0
            except Exception as exc:
                job.status, job.message = "failed", str(exc)
                job.log.append(traceback.format_exc())

        self.pool.submit(run)
        return job


runner = JobRunner()
