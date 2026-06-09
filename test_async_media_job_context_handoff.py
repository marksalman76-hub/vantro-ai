from pathlib import Path

TEXT = Path("backend/app/runtime/async_media_job_foundation.py").read_text(encoding="utf-8")

REQUIRED = [
    "media_job_id=job_id,",
    "durable_queue_job_id=job.get(\"durable_queue_job_id\") or \"\",",
    "task_id=job_id,",
]

for marker in REQUIRED:
    assert marker in TEXT, marker

print("ASYNC_MEDIA_JOB_CONTEXT_HANDOFF_TESTS_PASSED")
