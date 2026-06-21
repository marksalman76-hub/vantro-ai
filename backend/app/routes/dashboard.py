from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/credits")
async def get_credits(user_id: str = "test-user-1"):
    return {
        "user_id": user_id,
        "total_credits": 1000,
        "used_credits": 250,
        "remaining_credits": 750,
        "tier": "premium"
    }

@router.get("/media-jobs")
async def get_media_jobs(user_id: str = "test-user-1"):
    return {
        "user_id": user_id,
        "total_jobs": 12,
        "completed": 10,
        "processing": 1,
        "failed": 1,
        "jobs": [
            {
                "id": "job-001",
                "status": "completed",
                "video_url": "https://vantro.ai/videos/job-001.mp4",
                "created_at": "2026-06-20"
            }
        ]
    }

@router.get("/admin/stats")
async def get_admin_stats():
    return {
        "total_users": 156,
        "total_revenue": 45670,
        "active_subscriptions": 42,
        "videos_generated": 1247,
        "avg_video_length": 87.5
    }

@router.get("/admin/users")
async def get_admin_users():
    return {
        "total": 156,
        "users": [
            {"id": "user-1", "email": "admin@vantro.ai", "tier": "admin", "created_at": "2026-01-01"},
            {"id": "user-2", "email": "user@example.com", "tier": "premium", "created_at": "2026-03-15"}
        ]
    }
