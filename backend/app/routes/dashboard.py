from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
    return {
        "user_id": user.id,
        "total_credits": total,
        "used_credits": used,
        "remaining_credits": total - used,
        "tier": "starter",
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
