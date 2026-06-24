"""
Agent Worker — standalone entry point for the dedicated ECS Fargate service.

This is the process that handles all AI agent job execution (AgentJob rows).
It runs as a separate ECS service so it survives API container restarts and
can scale independently from the web tier.

Environment:
  DISABLE_INLINE_WORKER=1 must be set on the API container when this service
  is active, so the API doesn't also try to process jobs.

Usage:
  python agent_worker_entrypoint.py
"""
import asyncio
import logging
import os
import sys

# Ensure the backend package root is on sys.path regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("agent_worker_entrypoint")


async def main():
    logger.info("Vantro agent worker starting (standalone ECS mode)")

    # Boot skill RAG index on startup (non-blocking)
    try:
        from app.agents.agent_worker import _reindex_new_skills
        asyncio.create_task(_reindex_new_skills())
    except Exception as exc:
        logger.warning("Skill index boot skipped: %s", exc)

    from app.agents.agent_worker import run_agent_worker
    await run_agent_worker()


if __name__ == "__main__":
    asyncio.run(main())
