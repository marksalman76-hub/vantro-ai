import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.contact import router as contact_router
from app.routes.dashboard import router as dashboard_router
from app.routes.stripe import router as stripe_router
from app.services import heygen_service

logger = logging.getLogger(__name__)


async def _poll_heygen_jobs() -> None:
    """Background loop: check HeyGen status for all 'processing' jobs every 60 s."""
    from app.database import SessionLocal
    from app.models.workspace import MediaJob

    await asyncio.sleep(10)  # brief delay at startup
    while True:
        try:
            db = SessionLocal()
            try:
                jobs = (
                    db.query(MediaJob)
                    .filter(
                        MediaJob.status == "processing",
                        MediaJob.external_job_id.isnot(None),
                    )
                    .all()
                )
                for job in jobs:
                    result = await heygen_service.get_video_status(job.external_job_id)
                    if result["status"] == "completed":
                        job.status = "completed"
                        job.video_url = result["video_url"]
                        job.completed_at = datetime.utcnow()
                        logger.info("Job %s completed — video_url=%s", job.id, job.video_url)
                    elif result["status"] == "failed":
                        job.status = "failed"
                        job.error_message = result.get("error", "HeyGen processing failed")
                        logger.warning("Job %s failed: %s", job.id, job.error_message)
                if jobs:
                    db.commit()
            finally:
                db.close()
        except Exception as exc:
            logger.error("HeyGen poll error: %s", exc)

        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if heygen_service.is_configured():
        task = asyncio.create_task(_poll_heygen_jobs())
        logger.info("HeyGen polling worker started")
    else:
        task = None
        logger.info("HEYGEN_API_KEY not set — polling worker disabled")
    yield
    if task:
        task.cancel()


app = FastAPI(
    title="Vantro AI API",
    description="Enterprise AI video generation platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://vantro.ai", "https://www.vantro.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(contact_router)
app.include_router(dashboard_router)
app.include_router(stripe_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vantro-api"}


@app.get("/")
async def root():
    return {"name": "Vantro AI API", "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
