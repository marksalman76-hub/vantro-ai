"""
Agent Worker — async background loop that picks up and executes agent jobs.

Job lifecycle:
  pending           → picked up by worker → running → completed / failed
  pending_approval  → admin approves → approved → picked up by worker → running → ...
  approved          → picked up by worker → running → completed / failed

The worker runs inside the FastAPI lifespan (same process, asyncio background task).
For production scale this should move to a dedicated ECS worker service via SQS —
the same pattern used by the existing video worker. The interface is identical.
"""

import asyncio
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 5   # how often to check for new jobs
MAX_CONCURRENT_JOBS   = 3   # max parallel agent executions


async def _process_job(job_id: str) -> None:
    """Process a single agent job end-to-end."""

    # Local imports to avoid circular imports at module load
    from app.database import SessionLocal
    from app.models.agent_system import AgentJob
    from app.models.workspace import CreditsAccount, Workspace
    from app.agents.agent_prompts import get_agent_system_prompt
    from app.agents.agent_executor import execute_agent
    from app.agents.agent_registry import get_agent_credit_estimate, agent_exists

    db = SessionLocal()
    try:
        job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
        if not job:
            logger.warning("Worker: job %s not found", job_id)
            return

        # Guard: only process jobs that are still in a runnable state
        if job.status not in ("pending", "approved"):
            logger.debug("Worker: job %s already in status %s, skipping", job_id, job.status)
            return

        # Mark as running
        job.status = "running"
        job.updated_at = datetime.utcnow()
        db.commit()

        logger.info("Worker: executing agent=%s job=%s", job.agent_id, job_id)

        system_prompt = get_agent_system_prompt(job.agent_id)
        user_prompt   = job.input_data or ""

        # Parse optional context JSON stored in input_data
        context = {}
        try:
            parsed = json.loads(user_prompt)
            if isinstance(parsed, dict) and "prompt" in parsed:
                user_prompt = parsed["prompt"]
                context = parsed.get("context", {})
        except (json.JSONDecodeError, TypeError):
            pass

        output, provider_used = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: execute_agent(
                agent_id=job.agent_id,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                context=context,
            ),
        )

        # Credit deduction
        credit_cost = get_agent_credit_estimate(job.agent_id) if agent_exists(job.agent_id) else 1
        cred = (
            db.query(CreditsAccount)
            .join(Workspace, Workspace.id == CreditsAccount.workspace_id)
            .filter(Workspace.id == job.workspace_id)
            .first()
        )
        if cred:
            cred.used_credits = min(cred.total_credits, cred.used_credits + credit_cost)
            cred.updated_at = datetime.utcnow()

        now = datetime.utcnow()
        job.status       = "completed"
        job.output_data  = output
        job.credits_used = credit_cost
        job.updated_at   = now
        job.completed_at = now
        # Store provider used as metadata prefix in output
        job.output_data  = f"<!-- provider:{provider_used} -->\n{output}"
        db.commit()

        logger.info(
            "Worker: job %s completed via %s (%d credits deducted)",
            job_id, provider_used, credit_cost,
        )

    except Exception as exc:
        logger.error("Worker: job %s failed: %s", job_id, exc, exc_info=True)
        try:
            job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
            if job:
                job.status        = "failed"
                job.error_message = str(exc)[:2000]
                job.updated_at    = datetime.utcnow()
                db.commit()
        except Exception as db_exc:
            logger.error("Worker: failed to update job status: %s", db_exc)
    finally:
        db.close()


async def run_agent_worker() -> None:
    """
    Main worker loop. Polls the DB every POLL_INTERVAL_SECONDS for
    jobs in 'pending' or 'approved' state and processes them concurrently.
    """
    logger.info("Agent worker started (poll interval: %ds)", POLL_INTERVAL_SECONDS)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

    async def _guarded_process(job_id: str) -> None:
        async with semaphore:
            await _process_job(job_id)

    while True:
        try:
            from app.database import SessionLocal
            from app.models.agent_system import AgentJob

            db = SessionLocal()
            try:
                runnable = (
                    db.query(AgentJob.id)
                    .filter(AgentJob.status.in_(["pending", "approved"]))
                    .limit(MAX_CONCURRENT_JOBS * 2)
                    .all()
                )
                job_ids = [row.id for row in runnable]
            finally:
                db.close()

            if job_ids:
                logger.debug("Worker: found %d runnable job(s)", len(job_ids))
                tasks = [asyncio.create_task(_guarded_process(jid)) for jid in job_ids]
                await asyncio.gather(*tasks, return_exceptions=True)

        except asyncio.CancelledError:
            logger.info("Agent worker shutting down")
            break
        except Exception as exc:
            logger.error("Worker poll error: %s", exc, exc_info=True)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)
