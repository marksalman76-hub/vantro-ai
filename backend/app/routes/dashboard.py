import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Organization
from app.models.workspace import Workspace, CreditsAccount, MediaJob
from app.services import sqs_service, cache_service

router = APIRouter(prefix="/api", tags=["dashboard"])
security = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_user(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/credits")
async def get_credits(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    cache_key = cache_service.credits_key(user.id)

    cached = cache_service.get(cache_key)
    if cached:
        return cached

    result = (
        db.query(
            func.coalesce(func.sum(CreditsAccount.total_credits), 0).label("total"),
            func.coalesce(func.sum(CreditsAccount.used_credits), 0).label("used"),
        )
        .join(Workspace, Workspace.id == CreditsAccount.workspace_id)
        .join(Organization, Organization.id == Workspace.organization_id)
        .filter(Organization.owner_id == user.id)
        .one()
    )

    total = int(result.total)
    used = int(result.used)
    if total >= 300:
        tier = "business"
    elif total >= 200:
        tier = "growth"
    elif total >= 60:
        tier = "starter"
    else:
        tier = "free"
    payload = {
        "user_id": user.id,
        "total_credits": total,
        "used_credits": used,
        "remaining_credits": total - used,
        "tier": tier,
    }
    cache_service.set(cache_key, payload, ttl=60)
    return payload


@router.get("/media-jobs")
async def get_media_jobs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    cache_key = cache_service.media_jobs_key(user.id)

    cached = cache_service.get(cache_key)
    if cached:
        return cached

    jobs = (
        db.query(MediaJob)
        .join(Workspace, Workspace.id == MediaJob.workspace_id)
        .join(Organization, Organization.id == Workspace.organization_id)
        .filter(Organization.owner_id == user.id)
        .order_by(MediaJob.created_at.desc())
        .limit(20)
        .all()
    )

    status_counts = {"completed": 0, "processing": 0, "pending": 0, "failed": 0}
    for job in jobs:
        key = job.status if job.status in status_counts else "pending"
        status_counts[key] += 1

    payload = {
        "user_id": user.id,
        "total_jobs": len(jobs),
        "completed": status_counts["completed"],
        "processing": status_counts["processing"],
        "pending": status_counts["pending"],
        "failed": status_counts["failed"],
        "jobs": [
            {
                "id": j.id,
                "status": j.status,
                "video_url": j.video_url,
                "script": j.script[:100] + "..." if j.script and len(j.script) > 100 else j.script,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            }
            for j in jobs
        ],
    }
    cache_service.set(cache_key, payload, ttl=30)
    return payload


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Aggregated dashboard summary — credits + job counts in one call. Cached 60s."""
    from fastapi.responses import JSONResponse
    user = _get_user(credentials, db)

    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    workspace = None
    if org:
        workspace = db.query(Workspace).filter(Workspace.organization_id == org.id).first()

    workspace_id = workspace.id if workspace else user.id
    cache_key = f"dashboard:{workspace_id}"

    cached = cache_service.get(cache_key)
    if cached is not None:
        return JSONResponse(content=cached, headers={"Cache-Control": "max-age=60, private"})

    result = (
        db.query(
            func.coalesce(func.sum(CreditsAccount.total_credits), 0).label("total"),
            func.coalesce(func.sum(CreditsAccount.used_credits), 0).label("used"),
        )
        .join(Workspace, Workspace.id == CreditsAccount.workspace_id)
        .join(Organization, Organization.id == Workspace.organization_id)
        .filter(Organization.owner_id == user.id)
        .one()
    )
    total_credits = int(result.total)
    used_credits = int(result.used)

    job_count = 0
    if workspace:
        job_count = db.query(func.count(MediaJob.id)).filter(
            MediaJob.workspace_id == workspace.id
        ).scalar() or 0

    payload = {
        "user_id": user.id,
        "workspace_id": workspace_id,
        "total_credits": total_credits,
        "used_credits": used_credits,
        "remaining_credits": total_credits - used_credits,
        "total_jobs": job_count,
    }
    cache_service.set(cache_key, payload, ttl=60)
    return JSONResponse(content=payload, headers={"Cache-Control": "max-age=60, private"})


class CreateJobRequest(BaseModel):
    avatar_id: str
    voice_id: str
    script: str
    language: str = "en"
    tone: str = "professional"


