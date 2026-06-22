"""
Vantro Video Job Worker
=======================
Runs as a separate ECS Fargate service (1–10 tasks).
Consumes messages from SQS, submits jobs to HeyGen, polls for completion.

Each SQS message is processed by exactly one worker task (SQS visibility timeout
prevents duplicate processing). If this task crashes mid-job, the message
reappears after the visibility timeout and is retried by another task.

env vars required:
  DATABASE_URL          RDS connection string
  SQS_JOBS_QUEUE_URL    SQS FIFO queue URL
  HEYGEN_API_KEY        HeyGen API key
  HEYGEN_AVATAR_*       Avatar ID mappings
  HEYGEN_VOICE_*        Voice ID mappings
  REDIS_URL             (optional) Redis for cache invalidation
"""

import asyncio
import json
import logging
import os
import sys
import signal
from datetime import datetime

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.workspace import MediaJob
from app.services import heygen_service, sqs_service, cache_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("worker")

MAX_RETRIES = 3
POLL_INTERVAL = 30        # seconds between HeyGen status checks
MAX_POLL_MINUTES = 15     # give up after 15 min of polling
VISIBILITY_EXTEND = 300   # extend visibility by 5 min each poll cycle


def _get_db():
    return SessionLocal()


async def _process_job(message: dict) -> bool:
    """
    Process a single video job message end-to-end.
    Returns True if job completed (success or permanent failure).
    Returns False if a transient error occurred (message should stay in queue for retry).
    """
    receipt = message["ReceiptHandle"]
    try:
        body = json.loads(message["Body"])
    except (KeyError, json.JSONDecodeError) as e:
        logger.error("Malformed SQS message: %s", e)
        sqs_service.delete_job(receipt)
        return True  # discard unparseable messages

    job_id = body.get("job_id")
    if not job_id:
        logger.error("Message missing job_id: %s", body)
        sqs_service.delete_job(receipt)
        return True

    logger.info("Processing job %s", job_id)

    db = _get_db()
    try:
        job = db.query(MediaJob).filter(MediaJob.id == job_id).first()
        if not job:
            logger.warning("Job %s not found in DB — discarding", job_id)
            sqs_service.delete_job(receipt)
            return True

        # If already completed/failed (e.g. picked up twice), skip
        if job.status in ("completed", "failed"):
            logger.info("Job %s already %s — discarding duplicate", job_id, job.status)
            sqs_service.delete_job(receipt)
            return True

        # --- Step 1: Submit to HeyGen (if not already submitted) ---
        if not job.external_job_id:
            receive_count = int(
                (message.get("Attributes") or {}).get("ApproximateReceiveCount", 1)
            )
            if receive_count > MAX_RETRIES:
                _fail_job(db, job, "Max retries exceeded", cache_key_for(job))
                sqs_service.delete_job(receipt)
                return True

            external_id = await heygen_service.submit_video(
                avatar_id=body.get("avatar_id", job.avatar_id),
                voice_id=body.get("voice_id", job.voice_id),
                script=body.get("script", job.script),
                language=body.get("language", job.language or "en"),
            )
            if not external_id:
                logger.warning("HeyGen submit failed for job %s — will retry", job_id)
                return False  # leave message in queue; visibility timeout will retry

            job.external_job_id = external_id
            job.status = "processing"
            db.commit()
            logger.info("Job %s submitted to HeyGen: %s", job_id, external_id)

        # --- Step 2: Poll HeyGen until done ---
        elapsed = 0
        max_seconds = MAX_POLL_MINUTES * 60

        while elapsed < max_seconds:
            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL

            # Extend SQS visibility to prevent re-delivery while we poll
            sqs_service.extend_visibility(receipt, VISIBILITY_EXTEND)

            result = await heygen_service.get_video_status(job.external_job_id)
            status = result.get("status")
            logger.info("Job %s status: %s (elapsed %ds)", job_id, status, elapsed)

            if status == "completed":
                job.status = "completed"
                job.video_url = result.get("video_url")
                job.completed_at = datetime.utcnow()
                db.commit()
                _invalidate_cache(job_id, db)
                logger.info("Job %s completed — %s", job_id, job.video_url)
                sqs_service.delete_job(receipt)
                return True

            if status == "failed":
                _fail_job(db, job, result.get("error", "HeyGen reported failure"), job_id)
                sqs_service.delete_job(receipt)
                return True

        # Timed out
        _fail_job(db, job, f"Timed out after {MAX_POLL_MINUTES} minutes", job_id)
        sqs_service.delete_job(receipt)
        return True

    except Exception as exc:
        logger.exception("Unexpected error processing job %s: %s", job_id, exc)
        return False  # leave in queue for retry
    finally:
        db.close()


def _fail_job(db, job: MediaJob, reason: str, cache_hint: str = "") -> None:
    job.status = "failed"
    job.error_message = reason
    db.commit()
    logger.error("Job %s failed: %s", job.id, reason)
    if cache_hint:
        _invalidate_cache(cache_hint, db)


def _invalidate_cache(job_id: str, db) -> None:
    """Invalidate the user's media_jobs cache so dashboard refreshes immediately."""
    try:
        from app.models import Organization
        from app.models.workspace import Workspace
        job = db.query(MediaJob).filter(MediaJob.id == job_id).first()
        if not job:
            return
        workspace = db.query(Workspace).filter(Workspace.id == job.workspace_id).first()
        if not workspace:
            return
        org = db.query(Organization).filter(Organization.id == workspace.organization_id).first()
        if org:
            cache_service.delete(
                cache_service.media_jobs_key(org.owner_id),
                cache_service.credits_key(org.owner_id),
            )
    except Exception as e:
        logger.debug("Cache invalidation error: %s", e)


def cache_key_for(job: MediaJob) -> str:
    return job.id


async def run_worker() -> None:
    logger.info("Worker started — polling SQS queue")
    if not sqs_service.is_configured():
        logger.error("SQS_JOBS_QUEUE_URL is not set — worker has nothing to do. Exiting.")
        return
    if not heygen_service.is_configured():
        logger.warning("HEYGEN_API_KEY is not set — jobs will fail at submission")

    while True:
        messages = sqs_service.receive_jobs(max_messages=10, wait_seconds=20)
        if not messages:
            continue

        # Process messages concurrently (up to 10 at once per task)
        tasks = [asyncio.create_task(_process_job(m)) for m in messages]
        await asyncio.gather(*tasks, return_exceptions=True)


def _handle_shutdown(signum, frame):
    logger.info("Received signal %d — shutting down gracefully", signum)
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    asyncio.run(run_worker())
