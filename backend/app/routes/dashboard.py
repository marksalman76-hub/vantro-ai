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

    # Aggregate credits across all workspaces the user owns (via org ownership)
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
    tier = "free"
    if user.subscription_status in ("active", "trialing"):
        tier = "starter"
    return {
        "user_id": user.id,
        "total_credits": total,
        "used_credits": used,
        "remaining_credits": total - used,
        "tier": tier,
    }


@router.get("/media-jobs")
async def get_media_jobs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)

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

    return {
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


class CreateJobRequest(BaseModel):
    avatar_id: str
    voice_id: str
    script: str
    language: str = "en"
    tone: str = "professional"


@router.post("/media-jobs", status_code=201)
async def create_media_job(
    request: CreateJobRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)

    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        raise HTTPException(status_code=400, detail="No organization found. Complete onboarding first.")

    workspace = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="No workspace found. Complete onboarding first.")

    job = MediaJob(
        id=str(uuid.uuid4()),
        workspace_id=workspace.id,
        avatar_id=request.avatar_id,
        voice_id=request.voice_id,
        script=request.script,
        language=request.language,
        tone=request.tone,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()

    return {
        "id": job.id,
        "status": "pending",
        "message": "Video generation queued. This typically takes 2–5 minutes.",
        "created_at": job.created_at.isoformat(),
    }


@router.get("/admin/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar()
    total_jobs = db.query(func.count(MediaJob.id)).scalar()
    completed_jobs = db.query(func.count(MediaJob.id)).filter(MediaJob.status == "completed").scalar()
    return {
        "total_users": total_users,
        "total_media_jobs": total_jobs,
        "completed_media_jobs": completed_jobs,
        "total_revenue": 0,
        "active_subscriptions": 0,
    }


@router.get("/admin/users")
async def get_admin_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).limit(50).all()
    return {
        "total": len(users),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
    }
