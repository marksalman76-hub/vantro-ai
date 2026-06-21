from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models import User, CreditsAccount, MediaJob

router = APIRouter(prefix="/api", tags=["dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/credits")
async def get_credits(user_id: str, db: Session = Depends(get_db)):
    credits = db.query(CreditsAccount).filter(
        CreditsAccount.workspace_id == user_id
    ).first()
    
    if not credits:
        return {
            "total_credits": 0,
            "used_credits": 0,
            "remaining_credits": 0
        }
    
    return {
        "total_credits": credits.total_credits,
        "used_credits": credits.used_credits,
        "remaining_credits": credits.remaining_credits
    }

@router.get("/media-jobs")
async def get_media_jobs(user_id: str, db: Session = Depends(get_db)):
    jobs = db.query(MediaJob).filter(
        MediaJob.workspace_id == user_id
    ).order_by(MediaJob.created_at.desc()).limit(10).all()
    
    return [
        {
            "id": job.id,
            "avatar": job.avatar_id,
            "script": job.script,
            "status": job.status,
            "video_url": job.video_url,
            "created_at": job.created_at.isoformat()
        }
        for job in jobs
    ]

@router.get("/admin/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_videos = db.query(MediaJob).count()
    completed_videos = db.query(MediaJob).filter(
        MediaJob.status == "completed"
    ).count()
    
    return {
        "total_users": total_users,
        "total_revenue": 12450.00,
        "active_subscriptions": 23,
        "videos_generated": completed_videos
    }

@router.get("/admin/users")
async def get_admin_users(db: Session = Depends(get_db)):
    users = db.query(User).limit(50).all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
            "workspace_count": len(user.organizations) if hasattr(user, "organizations") else 0
        }
        for user in users
    ]
