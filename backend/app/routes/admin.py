import os
import logging
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
from app.models.agent_system import AgentJob, PackageDownload
from app.agents.agent_registry import (
    AGENT_CATALOGUE,
    INTERNAL_AGENTS,
    PACKAGE_AGENTS,
    TIER_ORDER,
    PURCHASABLE_AGENT_IDS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer(auto_error=False)

PLAN_CREDITS = {"starter": 60, "growth": 200, "business": 300}


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


def _require_admin(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    user = _get_user(credentials, db)
    admin_email = os.getenv("ADMIN_EMAIL", "")
    if not admin_email or user.email.lower() != admin_email.lower():
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def _resolve_client_record(user: User, db: Session) -> dict:
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    workspace = None
    credits = None
    if org:
        workspace = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    if workspace:
        credits = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == workspace.id).first()

    total = credits.total_credits if credits else 0
    used = credits.used_credits if credits else 0
    if total >= PLAN_CREDITS["business"]:
        tier = "business"
    elif total >= PLAN_CREDITS["growth"]:
        tier = "growth"
    elif total >= PLAN_CREDITS["starter"]:
        tier = "starter"
    else:
        tier = "free"

    return {
        "org": org,
        "workspace": workspace,
        "credits_obj": credits,
        "total_credits": total,
        "used_credits": used,
        "remaining_credits": total - used,
        "tier": tier,
    }


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    total_users   = db.query(func.count(User.id)).scalar() or 0
    active_subs   = db.query(func.count(User.id)).filter(User.subscription_status == "active").scalar() or 0
    trial_subs    = db.query(func.count(User.id)).filter(User.subscription_status == "trialing").scalar() or 0
    suspended     = db.query(func.count(User.id)).filter(User.is_active == False).scalar() or 0  # noqa: E712
    total_jobs    = db.query(func.count(MediaJob.id)).scalar() or 0
    completed     = db.query(func.count(MediaJob.id)).filter(MediaJob.status == "completed").scalar() or 0
    processing    = db.query(func.count(MediaJob.id)).filter(MediaJob.status == "processing").scalar() or 0
    pending       = db.query(func.count(MediaJob.id)).filter(MediaJob.status == "pending").scalar() or 0
    failed        = db.query(func.count(MediaJob.id)).filter(MediaJob.status == "failed").scalar() or 0

    return {
        "total_users": total_users,
        "active_subscriptions": active_subs,
        "trial_subscriptions": trial_subs,
        "paid_clients": active_subs,
        "suspended_accounts": suspended,
        "free_accounts": total_users - active_subs - trial_subs,
        "total_media_jobs": total_jobs,
        "completed_media_jobs": completed,
        "processing_media_jobs": processing,
        "pending_media_jobs": pending,
        "failed_media_jobs": failed,
        "queued_jobs": pending,
    }


# ─── Clients ──────────────────────────────────────────────────────────────────

@router.get("/users")
async def get_users(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    users = db.query(User).order_by(User.created_at.desc()).limit(100).all()
    return {
        "total": len(users),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "is_active": u.is_active,
                "subscription_status": u.subscription_status,
                "stripe_customer_id": u.stripe_customer_id,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
    }


@router.get("/clients")
async def get_clients(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    users = db.query(User).order_by(User.created_at.desc()).limit(200).all()
    result = []
    for u in users:
        rec = _resolve_client_record(u, db)
        job_count = 0
        last_job_at = None
        if rec["workspace"]:
            job_count = db.query(func.count(MediaJob.id)).filter(
                MediaJob.workspace_id == rec["workspace"].id
            ).scalar() or 0
            lj = (
                db.query(MediaJob)
                .filter(MediaJob.workspace_id == rec["workspace"].id)
                .order_by(MediaJob.created_at.desc())
                .first()
            )
            if lj and lj.created_at:
                last_job_at = lj.created_at.isoformat()

        result.append({
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "is_active": u.is_active,
            "subscription_status": u.subscription_status,
            "stripe_customer_id": u.stripe_customer_id,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "organization": rec["org"].name if rec["org"] else None,
            "tier": rec["tier"],
            "total_credits": rec["total_credits"],
            "used_credits": rec["used_credits"],
            "remaining_credits": rec["remaining_credits"],
            "total_jobs": job_count,
            "last_execution": last_job_at,
        })

    return {"total": len(result), "clients": result}


@router.get("/clients/{user_id}")
async def get_client_detail(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Client not found")

    rec = _resolve_client_record(user, db)
    jobs = []
    if rec["workspace"]:
        jobs = (
            db.query(MediaJob)
            .filter(MediaJob.workspace_id == rec["workspace"].id)
            .order_by(MediaJob.created_at.desc())
            .limit(50)
            .all()
        )

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "subscription_status": user.subscription_status,
        "stripe_customer_id": user.stripe_customer_id,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "organization": (
            {"id": rec["org"].id, "name": rec["org"].name, "slug": rec["org"].slug}
            if rec["org"] else None
        ),
        "workspace": (
            {"id": rec["workspace"].id, "name": rec["workspace"].name}
            if rec["workspace"] else None
        ),
        "credits": {
            "total": rec["total_credits"],
            "used": rec["used_credits"],
            "remaining": rec["remaining_credits"],
            "tier": rec["tier"],
        },
        "jobs": [
            {
                "id": j.id,
                "status": j.status,
                "script": (j.script[:80] + "…") if j.script and len(j.script) > 80 else j.script,
                "video_url": j.video_url,
                "error_message": j.error_message,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            }
            for j in jobs
        ],
    }


class CreditsAdjustment(BaseModel):
    amount: int
    reason: str = ""


@router.post("/clients/{user_id}/credits")
async def adjust_credits(
    user_id: str,
    body: CreditsAdjustment,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Client not found")

    rec = _resolve_client_record(user, db)
    if not rec["credits_obj"]:
        raise HTTPException(status_code=404, detail="No credits account found for this client")

    credits = rec["credits_obj"]
    credits.total_credits = max(0, credits.total_credits + body.amount)
    credits.updated_at = datetime.utcnow()
    db.commit()
    return {
        "success": True,
        "new_total": credits.total_credits,
        "new_remaining": credits.total_credits - credits.used_credits,
    }


@router.post("/clients/{user_id}/suspend")
async def suspend_client(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Client not found")
    user.is_active = False
    db.commit()
    return {"success": True}


@router.post("/clients/{user_id}/reactivate")
async def reactivate_client(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Client not found")
    user.is_active = True
    db.commit()
    return {"success": True}


# ─── Jobs ─────────────────────────────────────────────────────────────────────

@router.get("/jobs")
async def get_all_jobs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    jobs = db.query(MediaJob).order_by(MediaJob.created_at.desc()).limit(200).all()

    result = []
    for j in jobs:
        ws = db.query(Workspace).filter(Workspace.id == j.workspace_id).first()
        org = db.query(Organization).filter(Organization.id == ws.organization_id).first() if ws else None
        user = db.query(User).filter(User.id == org.owner_id).first() if org else None

        result.append({
            "id": j.id,
            "status": j.status,
            "script": (j.script[:80] + "…") if j.script and len(j.script) > 80 else j.script,
            "video_url": j.video_url,
            "error_message": j.error_message,
            "external_job_id": j.external_job_id,
            "avatar_id": j.avatar_id,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "client_id": user.id if user else None,
            "client_email": user.email if user else "unknown",
            "client_name": user.name if user else None,
            "workspace": ws.name if ws else None,
        })

    return {"total": len(result), "jobs": result}


@router.get("/jobs/{job_id}")
async def get_job_detail(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    job = db.query(MediaJob).filter(MediaJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    ws = db.query(Workspace).filter(Workspace.id == job.workspace_id).first()
    org = db.query(Organization).filter(Organization.id == ws.organization_id).first() if ws else None
    user = db.query(User).filter(User.id == org.owner_id).first() if org else None

    return {
        "id": job.id,
        "status": job.status,
        "script": job.script,
        "video_url": job.video_url,
        "error_message": job.error_message,
        "external_job_id": job.external_job_id,
        "avatar_id": job.avatar_id,
        "voice_id": job.voice_id,
        "language": job.language,
        "tone": job.tone,
        "facial_expressions": job.facial_expressions,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "client": {
            "id": user.id if user else None,
            "email": user.email if user else "unknown",
            "name": user.name if user else None,
        },
        "workspace": ws.name if ws else None,
    }


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    job = db.query(MediaJob).filter(MediaJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = "cancelled"
    job.updated_at = datetime.utcnow()
    db.commit()
    return {"success": True}


@router.post("/jobs/{job_id}/retry")
async def retry_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    job = db.query(MediaJob).filter(MediaJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = "pending"
    job.error_message = None
    job.updated_at = datetime.utcnow()
    db.commit()

    from app.services import sqs_service
    sqs_service.dispatch_video_job(
        job_id=job.id,
        avatar_id=job.avatar_id,
        voice_id=job.voice_id,
        script=job.script,
        language=job.language or "en",
        tone=job.tone or "professional",
    )
    return {"success": True}


# ─── Agents ───────────────────────────────────────────────────────────────────

@router.get("/agents")
async def get_agents(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return the full 27-agent catalogue with all metadata for admin use."""
    _require_admin(credentials, db)

    client_agents = [
        {
            "id": aid,
            "name": meta["name"],
            "category": meta["category"],
            "role": meta["role"],
            "architecture": meta["architecture"],
            "hitl_level": meta["hitl_default"],
            "min_package": meta["min_package"],
            "credit_estimate": meta["credit_estimate"],
            "capabilities": meta.get("capabilities", []),
            "visibility": "client",
        }
        for aid, meta in AGENT_CATALOGUE.items()
    ]

    internal = [
        {
            "id": aid,
            "name": meta["name"],
            "category": meta["category"],
            "role": meta["role"],
            "maps_to": meta.get("maps_to"),
            "visibility": "internal",
        }
        for aid, meta in INTERNAL_AGENTS.items()
    ]

    # Per-tier agent counts
    tier_counts = {tier: len(ids) for tier, ids in PACKAGE_AGENTS.items()}

    return {
        "total": len(client_agents),
        "internal_total": len(internal),
        "tier_counts": tier_counts,
        "agents": client_agents,
        "internal_layers": internal,
    }


@router.get("/agents/jobs")
async def admin_list_agent_jobs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin view of all agent jobs across all workspaces."""
    _require_admin(credentials, db)
    jobs = db.query(AgentJob).order_by(AgentJob.created_at.desc()).limit(500).all()

    result = []
    for j in jobs:
        ws = db.query(Workspace).filter(Workspace.id == j.workspace_id).first()
        org = db.query(Organization).filter(Organization.id == ws.organization_id).first() if ws else None
        user = db.query(User).filter(User.id == org.owner_id).first() if org else None
        result.append({
            "id": j.id,
            "agent_id": j.agent_id,
            "agent_name": j.agent_name,
            "status": j.status,
            "hitl_level": j.hitl_level,
            "credits_used": j.credits_used,
            "error_message": j.error_message,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "client_email": user.email if user else "unknown",
            "workspace": ws.name if ws else None,
        })
    return {"total": len(result), "jobs": result}


@router.post("/agents/jobs/{job_id}/approve")
async def admin_approve_agent_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin approves a HITL-3 pending_approval agent job."""
    _require_admin(credentials, db)
    job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Agent job not found")
    if job.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Job is in status '{job.status}', not pending_approval")
    job.status = "approved"
    job.updated_at = datetime.utcnow()
    db.commit()
    return {"success": True, "job_id": job_id, "new_status": "approved"}


@router.post("/agents/jobs/{job_id}/reject")
async def admin_reject_agent_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin rejects a HITL-3 pending_approval agent job."""
    _require_admin(credentials, db)
    job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Agent job not found")
    job.status = "rejected"
    job.updated_at = datetime.utcnow()
    db.commit()
    return {"success": True, "job_id": job_id, "new_status": "rejected"}


@router.get("/packages/downloads")
async def admin_list_downloads(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin view of all OTC package downloads."""
    _require_admin(credentials, db)
    downloads = db.query(PackageDownload).order_by(PackageDownload.created_at.desc()).limit(500).all()

    result = []
    for d in downloads:
        ws = db.query(Workspace).filter(Workspace.id == d.workspace_id).first()
        org = db.query(Organization).filter(Organization.id == ws.organization_id).first() if ws else None
        user = db.query(User).filter(User.id == org.owner_id).first() if org else None
        result.append({
            "id": d.id,
            "package_name": d.package_name,
            "otc_code": d.otc_code,
            "is_used": d.is_used,
            "used_at": d.used_at.isoformat() if d.used_at else None,
            "expires_at": d.expires_at.isoformat() if d.expires_at else None,
            "ip_address": d.ip_address,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "client_email": user.email if user else "unknown",
            "workspace": ws.name if ws else None,
        })
    return {"total": len(result), "downloads": result}


# ─── Provider Health ──────────────────────────────────────────────────────────

@router.get("/providers")
async def get_providers(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)

    def provider_status(env_var: str) -> str:
        return "ready" if os.getenv(env_var) else "not_configured"

    return {
        "providers": [
            {
                "name": "HeyGen",
                "category": "Video / Avatar",
                "configured": bool(os.getenv("HEYGEN_API_KEY")),
                "readiness": provider_status("HEYGEN_API_KEY"),
                "notes": "Primary video generation and avatar presenter",
                "role": "primary",
            },
            {
                "name": "Stripe",
                "category": "Billing",
                "configured": bool(os.getenv("STRIPE_SECRET_KEY")),
                "readiness": provider_status("STRIPE_SECRET_KEY"),
                "notes": "Subscriptions, checkouts, and billing portal",
                "role": "primary",
            },
            {
                "name": "AWS SQS",
                "category": "Queue / Worker",
                "configured": bool(os.getenv("SQS_JOBS_QUEUE_URL")),
                "readiness": provider_status("SQS_JOBS_QUEUE_URL"),
                "notes": "Async job queue for video processing",
                "role": "primary",
            },
            {
                "name": "Redis (ElastiCache)",
                "category": "Cache / Rate Limiting",
                "configured": bool(os.getenv("REDIS_URL")),
                "readiness": provider_status("REDIS_URL"),
                "notes": "API rate limiting and response caching",
                "role": "primary",
            },
            {
                "name": "ElevenLabs",
                "category": "Voice / Audio",
                "configured": bool(os.getenv("ELEVENLABS_API_KEY")),
                "readiness": provider_status("ELEVENLABS_API_KEY"),
                "notes": "Voice synthesis — future provider",
                "role": "future",
            },
            {
                "name": "Runway",
                "category": "Video Generation",
                "configured": bool(os.getenv("RUNWAY_API_KEY")),
                "readiness": provider_status("RUNWAY_API_KEY"),
                "notes": "Cinematic video generation — future provider",
                "role": "future",
            },
        ]
    }


# ─── Infrastructure ───────────────────────────────────────────────────────────

@router.get("/infrastructure")
async def get_infrastructure(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    db_url = os.getenv("DATABASE_URL", "")

    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "account_id": "685570573617",
        "services": [
            {"name": "RDS PostgreSQL",      "status": "configured" if "postgres" in db_url else "not_configured", "detail": "Primary database — RDS via Secrets Manager"},
            {"name": "SQS Job Queue",        "status": "configured" if os.getenv("SQS_JOBS_QUEUE_URL") else "not_configured", "detail": "FIFO queue for async video job processing"},
            {"name": "ElastiCache Redis",    "status": "configured" if os.getenv("REDIS_URL") else "not_configured", "detail": "t3.micro Redis 7.0 for rate limiting and caching"},
            {"name": "AWS Secrets Manager",  "status": "configured", "detail": "All secrets injected via ECS task definition"},
            {"name": "ECS API Service",      "status": "running",    "detail": "trance-formation-api — Fargate 256 CPU / 512 MB"},
            {"name": "ECS Worker Service",   "status": "running",    "detail": "vantro-worker — Fargate 512 CPU / 1024 MB"},
            {"name": "ALB",                  "status": "configured", "detail": "api.vantro.ai — HTTPS via ACM cert"},
            {"name": "WAF",                  "status": "configured", "detail": "AWS managed rules + IP rate limiting"},
            {"name": "CloudWatch Alarms",    "status": "configured", "detail": "CPU, memory, error alarms → SNS email"},
            {"name": "ACM Certificate",      "status": "configured", "detail": "api.vantro.ai — DNS validated"},
            {"name": "ECR",                  "status": "configured", "detail": "trance-formation/api and trance-formation/worker"},
            {"name": "IAM Roles",            "status": "configured", "detail": "ecsTaskExecutionRole + ecsTaskRole"},
        ],
    }
