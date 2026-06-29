import os
import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional, List

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Organization
from app.models.workspace import Workspace, CreditsAccount, MediaJob
from app.models.agent_system import AgentJob, PackageDownload, WorkspaceIntegration
from app.models.audit_log import AuditLog
from app.models import Announcement, AgentChangelog, SystemStatus
from app.agents.agent_registry import (
    AGENT_CATALOGUE,
    INTERNAL_AGENTS,
    PACKAGE_AGENTS,
    TIER_ORDER,
    PURCHASABLE_AGENT_IDS,
)
from app.runtime.audio_visual_provider_stack import (
    full_provider_stack_status,
    provider_config_status,
)
from app.services.email_service import send_approval_result

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
    # Accept: is_admin flag (DB-driven multi-admin) OR the bootstrap ADMIN_EMAIL env var
    is_admin = getattr(user, "is_admin", False)
    email_match = admin_email and user.email.lower() == admin_email.lower()
    if not is_admin and not email_match:
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


def _has_active_integration(db: Session, workspace_id: str | None, integration_key: str) -> bool:
    if not workspace_id:
        return False
    return (
        db.query(WorkspaceIntegration.id)
        .filter(
            WorkspaceIntegration.workspace_id == workspace_id,
            WorkspaceIntegration.integration_key == integration_key,
            WorkspaceIntegration.is_active == True,
        )
        .first()
        is not None
    )


def _provider_configured(*env_vars: str) -> bool:
    return any(bool(os.getenv(env_var)) for env_var in env_vars)


def _platform_provider_health(user: User, db: Session) -> list[dict]:
    client_record = _resolve_client_record(user, db)
    workspace = client_record.get("workspace")
    workspace_id = getattr(workspace, "id", None)
    github_configured = _provider_configured("GITHUB_TOKEN", "GH_TOKEN") or _has_active_integration(
        db,
        workspace_id,
        "COMPOSIO_API_KEY",
    )

    def readiness(configured: bool) -> str:
        return "ready" if configured else "not_configured"

    providers = [
        {
            "name": "HeyGen",
            "category": "Video / Avatar",
            "configured": _provider_configured("HEYGEN_API_KEY"),
            "readiness": readiness(_provider_configured("HEYGEN_API_KEY")),
            "notes": "Primary video generation and avatar presenter",
            "role": "primary",
        },
        {
            "name": "Stripe",
            "category": "Billing",
            "configured": _provider_configured("STRIPE_SECRET_KEY"),
            "readiness": readiness(_provider_configured("STRIPE_SECRET_KEY")),
            "notes": "Subscriptions, checkouts, and billing portal",
            "role": "primary",
        },
        {
            "name": "AWS SQS",
            "category": "Queue / Worker",
            "configured": _provider_configured("SQS_JOBS_QUEUE_URL"),
            "readiness": readiness(_provider_configured("SQS_JOBS_QUEUE_URL")),
            "notes": "Async job queue for video processing",
            "role": "primary",
        },
        {
            "name": "Redis (ElastiCache)",
            "category": "Cache / Rate Limiting",
            "configured": _provider_configured("REDIS_URL"),
            "readiness": readiness(_provider_configured("REDIS_URL")),
            "notes": "API rate limiting and response caching",
            "role": "primary",
        },
        {
            "name": "GitHub",
            "category": "Code / Repository",
            "configured": github_configured,
            "readiness": readiness(github_configured),
            "notes": "Repository automation via GitHub token or Composio GitHub app connection",
            "role": "primary",
        },
        {
            "name": "ElevenLabs",
            "category": "Voice / Audio",
            "configured": _provider_configured("ELEVENLABS_API_KEY"),
            "readiness": readiness(_provider_configured("ELEVENLABS_API_KEY")),
            "notes": "Voice synthesis - future provider",
            "role": "future",
        },
        {
            "name": "Runway",
            "category": "Video Generation",
            "configured": _provider_configured("RUNWAY_API_KEY"),
            "readiness": readiness(_provider_configured("RUNWAY_API_KEY")),
            "notes": "Cinematic video generation - future provider",
            "role": "future",
        },
    ]

    creative_provider_entries = [
        ("higgsfield", "Higgsfield", "Video Generation", "Creative video generation provider", "primary"),
        ("nano_banana", "Nano Banana", "Image Generation", "Creative image generation provider", "primary"),
    ]
    for provider_key, name, category, notes, role in creative_provider_entries:
        status = provider_config_status(provider_key)
        providers.append({
            "name": name,
            "category": category,
            "configured": bool(status.get("configured")),
            "readiness": readiness(bool(status.get("configured"))),
            "notes": notes,
            "role": role,
            "models": status.get("models", []),
            "agents": status.get("agents", []),
            "live_execution_enabled": bool(status.get("live_execution_enabled")),
            "credential_values_exposed": False,
        })

    return providers


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
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    base_q = db.query(User)
    total = base_q.count()
    users = base_q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
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
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    base_q = db.query(User)
    total_count = base_q.count()
    users = base_q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
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

    return {"total": total_count, "skip": skip, "limit": limit, "clients": result}


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
    amount: int = Field(..., ge=-10000, le=10000, description="Credits to add (positive) or deduct (negative)")
    reason: str = Field(default="", max_length=500)


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
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    base_q = db.query(MediaJob)
    total = base_q.count()
    jobs = base_q.order_by(MediaJob.created_at.desc()).offset(skip).limit(limit).all()

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

    return {"total": total, "skip": skip, "limit": limit, "jobs": result}


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
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str = Query("", description="Filter by job status"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin view of all agent jobs across all workspaces."""
    _require_admin(credentials, db)
    base_q = db.query(AgentJob)
    if status:
        base_q = base_q.filter(AgentJob.status == status)
    total = base_q.count()
    jobs = base_q.order_by(AgentJob.created_at.desc()).offset(skip).limit(limit).all()

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
    return {"total": total, "skip": skip, "limit": limit, "jobs": result}


@router.post("/agents/jobs/{job_id}/approve")
async def admin_approve_agent_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin approves a pending_approval or pending_financial_review agent job."""
    _require_admin(credentials, db)
    job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Agent job not found")
    if job.status not in ("pending_approval", "pending_financial_review"):
        raise HTTPException(status_code=400, detail=f"Job is in status '{job.status}', not awaiting approval")
    # Financial review jobs: output already exists — release to completed
    if job.status == "pending_financial_review":
        job.status = "completed"
        if not job.completed_at:
            job.completed_at = datetime.utcnow()
    else:
        job.status = "approved"
    job.updated_at = datetime.utcnow()
    db.commit()

    # Notify user of approval — look up user via workspace → org (AgentJob has no user_id field)
    try:
        org = db.query(Organization).join(Workspace, Workspace.organization_id == Organization.id).filter(Workspace.id == job.workspace_id).first()
        if org:
            job_owner = db.query(User).filter(User.id == org.owner_id).first()
            if job_owner:
                send_approval_result(job_owner.email, job.agent_id, approved=True)
    except Exception:
        logger.exception("Failed to send approval email for job %s", job_id)

    return {"success": True, "job_id": job_id, "new_status": "approved"}


@router.post("/agents/jobs/{job_id}/reject")
async def admin_reject_agent_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin rejects a pending_approval or pending_financial_review agent job."""
    _require_admin(credentials, db)
    job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Agent job not found")
    reason = ""
    job.status = "rejected"
    job.updated_at = datetime.utcnow()
    db.commit()

    # Notify user of rejection — look up user via workspace → org (AgentJob has no user_id field)
    try:
        org = db.query(Organization).join(Workspace, Workspace.organization_id == Organization.id).filter(Workspace.id == job.workspace_id).first()
        if org:
            job_owner = db.query(User).filter(User.id == org.owner_id).first()
            if job_owner:
                send_approval_result(job_owner.email, job.agent_id, approved=False, reason=reason)
    except Exception:
        logger.exception("Failed to send rejection email for job %s", job_id)

    return {"success": True, "job_id": job_id, "new_status": "rejected"}


@router.get("/packages/downloads")
async def admin_list_downloads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin view of all OTC package downloads."""
    _require_admin(credentials, db)
    base_q = db.query(PackageDownload)
    total = base_q.count()
    downloads = base_q.order_by(PackageDownload.created_at.desc()).offset(skip).limit(limit).all()

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
    return {"total": total, "skip": skip, "limit": limit, "downloads": result}


# ─── Provider Health ──────────────────────────────────────────────────────────

@router.get("/providers")
async def get_providers(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _require_admin(credentials, db)
    provider_stack = full_provider_stack_status()
    return {
        "providers": _platform_provider_health(user, db),
        "provider_stack": provider_stack,
        "creative_provider_routing": provider_stack["creative_provider_routing"],
        "credential_values_exposed": False,
    }

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


# ─── Admin Run Agent (no package/credit restrictions) ─────────────────────────

class AdminRunRequest(BaseModel):
    prompt: str
    context: dict = {}


@router.post("/agents/{agent_id}/run")
async def admin_run_agent(
    agent_id: str,
    body: AdminRunRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin can run any agent without package, credit, or workspace restrictions."""
    import uuid as _uuid
    import json as _json

    admin = _require_admin(credentials, db)

    from app.agents.agent_registry import normalize_agent_id
    norm_id = normalize_agent_id(agent_id)
    if norm_id not in AGENT_CATALOGUE:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    from app.runtime.creative_provider_routing import (
        is_creative_agent,
        resolve_creative_provider_route,
    )

    run_context = dict(body.context or {})
    if is_creative_agent(norm_id):
        media_request = run_context.get("media_request") if isinstance(run_context.get("media_request"), dict) else {}
        route_media_type = media_request.get("media_type") or media_request.get("type") or run_context.get("media_type") or "both"
        run_context["creative_provider_route"] = resolve_creative_provider_route(
            agent_id=norm_id,
            media_type=route_media_type,
            video_quality=media_request.get("video_quality") or run_context.get("video_quality") or "",
            image_tier=media_request.get("image_tier") or run_context.get("image_tier") or "",
            request_context=run_context,
        )

    meta = AGENT_CATALOGUE[norm_id]
    hitl = meta["hitl_default"]

    # Get or create admin workspace
    ws = db.query(Workspace).filter(Workspace.owner_id == admin.id).first()
    if not ws:
        ws = Workspace(
            id=str(_uuid.uuid4()),
            owner_id=admin.id,
            name="Admin Workspace",
            plan="enterprise",
            created_at=datetime.utcnow(),
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)

    now = datetime.utcnow()
    job = AgentJob(
        id=str(_uuid.uuid4()),
        workspace_id=ws.id,
        agent_id=norm_id,
        agent_name=meta["name"],
        status="pending",
        hitl_level=hitl,
        input_data=_json.dumps({"prompt": body.prompt[:10_000], "context": run_context}),
        credits_used=0,
        created_at=now,
        updated_at=now,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "agent_id": norm_id,
        "agent_name": meta["name"],
        "status": job.status,
        "hitl_level": hitl,
        "message": "Job queued. Admin run bypasses package and credit restrictions.",
    }


@router.get("/agents/jobs/{job_id}")
async def admin_get_agent_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "agent_id": job.agent_id,
        "agent_name": job.agent_name,
        "status": job.status,
        "hitl_level": job.hitl_level,
        "output": job.output_data,
        "error_message": job.error_message,
        "credits_used": job.credits_used,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


# ─── Support Tickets (Admin) ──────────────────────────────────────────────────

@router.get("/support/tickets")
async def admin_list_support_tickets(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin view of all support tickets."""
    _require_admin(credentials, db)
    rows = db.execute(
        text("SELECT * FROM support_tickets ORDER BY created_at DESC LIMIT 200")
    ).fetchall()
    return {"tickets": [dict(r._mapping) for r in rows]}


@router.patch("/support/tickets/{ticket_id}")
async def admin_update_ticket(
    ticket_id: str,
    body: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin updates support ticket status."""
    _require_admin(credentials, db)
    new_status = body.get("status", "resolved")
    db.execute(
        text("UPDATE support_tickets SET status = :status, updated_at = :ts WHERE id = :id"),
        {"status": new_status, "ts": datetime.utcnow(), "id": ticket_id},
    )
    db.commit()
    return {"ticket_id": ticket_id, "status": new_status}


# ─── Packages — Deploy Unlimited ─────────────────────────────────────────────

class DeployUnlimitedRequest(BaseModel):
    user_id: str = ""
    reason: str = "Admin unlimited deployment"


@router.post("/packages/deploy-unlimited")
async def deploy_unlimited_credits(
    body: DeployUnlimitedRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Grant 9999 credits to admin account or a specified user."""
    admin = _require_admin(credentials, db)

    target_id = body.user_id or admin.id
    user = db.query(User).filter(User.id == target_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")

    rec = _resolve_client_record(user, db)
    if not rec["credits_obj"]:
        raise HTTPException(status_code=404, detail="No credits account found for user")

    credits = rec["credits_obj"]
    credits.total_credits = 9999
    credits.updated_at = datetime.utcnow()
    db.commit()
    logger.info(
        "Admin %s deployed unlimited credits to user %s. Reason: %s",
        admin.email, user.email, body.reason,
    )
    return {
        "success": True,
        "target_user": user.email,
        "new_total": 9999,
        "message": "Unlimited package deployed. Credits set to 9999.",
    }


# ── Audit Logs ────────────────────────────────────────────────────────────────

@router.get("/audit-logs")
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: str | None = Query(None),
    action: str | None = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    total = q.count()
    logs = q.offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": [
            {
                "id": lg.id,
                "user_id": lg.user_id,
                "action": lg.action,
                "resource_type": lg.resource_type,
                "resource_id": lg.resource_id,
                "ip_address": lg.ip_address,
                "created_at": lg.created_at.isoformat() if lg.created_at else None,
                "extra": lg.extra,
            }
            for lg in logs
        ],
    }


# ── Admin user management ─────────────────────────────────────────────────────

@router.post("/users/{user_id}/grant-admin")
async def grant_admin(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Grant is_admin flag to a user — enables multi-admin without changing ADMIN_EMAIL."""
    admin = _require_admin(credentials, db)
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_admin = True
    db.commit()
    logger.info("Admin %s granted admin to user %s (%s)", admin.email, target.email, user_id)
    return {"success": True, "user_id": user_id, "email": target.email, "is_admin": True}


@router.post("/users/{user_id}/revoke-admin")
async def revoke_admin(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin = _require_admin(credentials, db)
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_admin = False
    db.commit()
    logger.info("Admin %s revoked admin from user %s (%s)", admin.email, target.email, user_id)
    return {"success": True, "user_id": user_id, "email": target.email, "is_admin": False}


# ─── Skill RAG ────────────────────────────────────────────────────────────────

@router.post("/skills/index")
async def trigger_skill_indexing(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Trigger skill re-indexing (admin only)."""
    _require_admin(credentials, db)
    from app.services.skill_indexer import index_all_skills
    result = index_all_skills(db)
    return result


@router.get("/skills/chunks")
async def list_skill_chunks(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """List indexed skill names and chunk counts (admin only)."""
    _require_admin(credentials, db)
    from app.models.skill_chunk import SkillChunk
    rows = db.query(
        SkillChunk.skill_name,
        func.count(SkillChunk.id).label("chunks"),
    ).group_by(SkillChunk.skill_name).all()
    return {"skills": [{"name": r.skill_name, "chunks": r.chunks} for r in rows]}


# ── Agent Examples (few-shot quality system) ──────────────────────────────────

class AgentExampleCreate(BaseModel):
    task_description: str
    exemplary_output: str
    quality_note: str | None = None
    source_job_id: str | None = None


class AgentExampleUpdate(BaseModel):
    task_description: str | None = None
    exemplary_output: str | None = None
    quality_note: str | None = None
    is_active: bool | None = None


@router.get("/agents/{agent_id}/examples")
async def list_agent_examples(
    agent_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """List all examples for an agent. Admin only."""
    _require_admin(credentials, db)
    from app.models.agent_example import AgentExample
    rows = (
        db.query(AgentExample)
        .filter(AgentExample.agent_id == agent_id)
        .order_by(AgentExample.created_at.desc())
        .all()
    )
    return {
        "agent_id": agent_id,
        "examples": [
            {
                "id": r.id,
                "task_description": r.task_description[:200],
                "quality_note": r.quality_note,
                "is_active": r.is_active,
                "source_job_id": r.source_job_id,
                "created_at": r.created_at,
            }
            for r in rows
        ],
    }


@router.post("/agents/{agent_id}/examples", status_code=201)
async def add_agent_example(
    agent_id: str,
    body: AgentExampleCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Add a curated few-shot example for an agent. Admin only."""
    admin = _require_admin(credentials, db)
    from app.models.agent_example import AgentExample
    from app.agents.agent_registry import normalize_agent_id
    norm_id = normalize_agent_id(agent_id)
    if norm_id not in AGENT_CATALOGUE:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    ex = AgentExample(
        agent_id=norm_id,
        task_description=body.task_description,
        exemplary_output=body.exemplary_output,
        quality_note=body.quality_note,
        source_job_id=body.source_job_id,
        created_by=admin.id,
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return {"id": ex.id, "agent_id": ex.agent_id}


@router.put("/agents/{agent_id}/examples/{example_id}")
async def update_agent_example(
    agent_id: str,
    example_id: int,
    body: AgentExampleUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Update or deactivate an example. Admin only."""
    _require_admin(credentials, db)
    from app.models.agent_example import AgentExample
    ex = (
        db.query(AgentExample)
        .filter(AgentExample.id == example_id, AgentExample.agent_id == agent_id)
        .first()
    )
    if not ex:
        raise HTTPException(status_code=404, detail="Example not found")
    for field, val in body.dict(exclude_none=True).items():
        setattr(ex, field, val)
    db.commit()
    return {"id": ex.id, "is_active": ex.is_active}


@router.delete("/agents/{agent_id}/examples/{example_id}", status_code=204)
async def delete_agent_example(
    agent_id: str,
    example_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Hard delete an example. Admin only."""
    _require_admin(credentials, db)
    from app.models.agent_example import AgentExample
    deleted = (
        db.query(AgentExample)
        .filter(AgentExample.id == example_id, AgentExample.agent_id == agent_id)
        .delete()
    )
    db.commit()
    if not deleted:
        raise HTTPException(status_code=404, detail="Example not found")


@router.post("/agents/{agent_id}/examples/from-job/{job_id}", status_code=201)
async def promote_job_to_example(
    agent_id: str,
    job_id: str,
    quality_note: str | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Promote a past agent job's output as a few-shot quality example. Admin only."""
    admin = _require_admin(credentials, db)
    from app.models.agent_example import AgentExample
    from app.agents.agent_registry import normalize_agent_id

    job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
    if not job or not job.output_data:
        raise HTTPException(status_code=404, detail="Job not found or has no output")

    # Extract task description from input_data JSON; fall back to raw string
    task_description = ""
    if job.input_data:
        try:
            import json as _json
            parsed = _json.loads(job.input_data)
            task_description = str(parsed.get("prompt", ""))[:500]
        except Exception:
            task_description = job.input_data[:500]

    norm_id = normalize_agent_id(agent_id)
    ex = AgentExample(
        agent_id=norm_id,
        task_description=task_description,
        exemplary_output=(job.output_data or "")[:3000],
        quality_note=quality_note,
        source_job_id=job_id,
        created_by=admin.id,
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return {"id": ex.id, "agent_id": ex.agent_id, "source_job_id": job_id}


# ─── Security Alerts ──────────────────────────────────────────────────────────

_SECURITY_ACTIONS = {
    "login_failed", "security_alert", "agent_tamper", "reverse_engineering",
    "package_redeployment", "prompt_extraction", "malicious_request",
    "credential_attack", "suspicious_automation", "account_locked",
    "device_revoked", "session_revoked",
}

_SEVERITY_MAP: dict[str, str] = {
    "agent_tamper": "critical",
    "credential_attack": "critical",
    "malicious_request": "high",
    "reverse_engineering": "high",
    "package_redeployment": "high",
    "prompt_extraction": "medium",
    "suspicious_automation": "medium",
    "login_failed": "low",
    "security_alert": "medium",
    "account_locked": "info",
    "device_revoked": "info",
    "session_revoked": "info",
}

_ALERT_LABELS: dict[str, str] = {
    "agent_tamper": "Agent tamper attempt",
    "credential_attack": "Credential attack detected",
    "malicious_request": "Malicious request blocked",
    "reverse_engineering": "Reverse-engineering attempt",
    "package_redeployment": "Package redeployment attempt",
    "prompt_extraction": "Prompt extraction attempt",
    "suspicious_automation": "Suspicious automation detected",
    "login_failed": "Failed login attempt",
    "security_alert": "Security alert",
    "account_locked": "Account locked",
    "device_revoked": "Device revoked",
    "session_revoked": "Session revoked",
}


def _safe_alert_detail(log: AuditLog) -> str:
    """Return human-readable detail — never raw exploit payloads or secrets."""
    extra = log.extra or {}
    parts = []
    if extra.get("alert_type"):
        parts.append(str(extra["alert_type"])[:100])
    if extra.get("reason"):
        parts.append(str(extra["reason"])[:200])
    if extra.get("agent_id"):
        parts.append(f"Agent: {extra['agent_id']}")
    # Partial IP only — never full IP in the response
    ip = extra.get("ip_address") or log.ip_address or ""
    if ip:
        octets = ip.split(".")
        parts.append(f"IP prefix: {'.'.join(octets[:2])}.*.*" if len(octets) >= 2 else "IP: redacted")
    return ". ".join(p for p in parts if p) or "Security event recorded."


@router.get("/security/alerts")
async def list_security_alerts(
    severity: str | None = Query(None, description="critical|high|medium|low|info"),
    status: str | None = Query(None, description="open|acknowledged"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)

    ack_ids = {
        str(r.resource_id)
        for r in db.query(AuditLog).filter(AuditLog.action == "security_alert_acknowledged").all()
        if r.resource_id
    }

    alerts: list[dict] = []

    # Synthesize alerts from financial-review agent jobs
    financial_jobs = (
        db.query(AgentJob)
        .filter(AgentJob.status == "pending_financial_review")
        .order_by(AgentJob.created_at.desc())
        .limit(100)
        .all()
    )
    for job in financial_jobs:
        aid = f"fin_{job.id}"
        sev = "medium"
        if severity and sev != severity:
            continue
        is_ack = aid in ack_ids
        if status == "acknowledged" and not is_ack:
            continue
        if status == "open" and is_ack:
            continue
        ws = db.query(Workspace).filter(Workspace.id == job.workspace_id).first()
        org = db.query(Organization).filter(Organization.id == ws.organization_id).first() if ws else None
        user = db.query(User).filter(User.id == org.owner_id).first() if org else None
        alerts.append({
            "id": aid,
            "severity": sev,
            "type": "financial_review_flagged",
            "label": "Financial action flagged for review",
            "client_email": user.email if user else "unknown",
            "client_id": user.id if user else None,
            "related_job_id": job.id,
            "related_agent": job.agent_name,
            "status": "acknowledged" if is_ack else "open",
            "detail": f"Agent job '{job.agent_name}' output flagged for financial review.",
            "detected_at": job.created_at.isoformat() if job.created_at else None,
        })

    # Derive alerts from audit log security actions
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.action.in_(_SECURITY_ACTIONS))
        .order_by(AuditLog.created_at.desc())
        .limit(500)
        .all()
    )
    for log in logs:
        aid = str(log.id)
        sev = _SEVERITY_MAP.get(log.action, "info")
        if severity and sev != severity:
            continue
        is_ack = aid in ack_ids
        if status == "acknowledged" and not is_ack:
            continue
        if status == "open" and is_ack:
            continue
        user = db.query(User).filter(User.id == log.user_id).first() if log.user_id else None
        alerts.append({
            "id": aid,
            "severity": sev,
            "type": log.action,
            "label": _ALERT_LABELS.get(log.action, "Security event"),
            "client_email": user.email if user else "unknown",
            "client_id": user.id if user else None,
            "related_job_id": log.resource_id if log.resource_type == "agent_job" else None,
            "related_agent": (log.extra or {}).get("agent_id"),
            "status": "acknowledged" if is_ack else "open",
            "detail": _safe_alert_detail(log),
            "detected_at": log.created_at.isoformat() if log.created_at else None,
        })

    alerts.sort(key=lambda a: a["detected_at"] or "", reverse=True)
    total = len(alerts)
    return {"total": total, "alerts": alerts[skip: skip + limit]}


@router.get("/security/stats")
async def security_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)

    ack_count = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "security_alert_acknowledged"
    ).scalar() or 0

    raw_security = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action.in_(_SECURITY_ACTIONS)
    ).scalar() or 0

    critical = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action.in_({"agent_tamper", "credential_attack"})
    ).scalar() or 0

    financial_review = db.query(func.count(AgentJob.id)).filter(
        AgentJob.status == "pending_financial_review"
    ).scalar() or 0

    pending_approvals = db.query(func.count(AgentJob.id)).filter(
        AgentJob.status.in_({"pending_approval", "pending_financial_review"})
    ).scalar() or 0

    return {
        "open_security_alerts": max(0, raw_security + financial_review - ack_count),
        "critical_alerts": critical,
        "financial_review_flagged": financial_review,
        "pending_approvals": pending_approvals,
    }


class AcknowledgeAlertRequest(BaseModel):
    note: str = ""


@router.post("/security/alerts/{alert_id}/acknowledge")
async def acknowledge_security_alert(
    alert_id: str,
    body: AcknowledgeAlertRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin = _require_admin(credentials, db)
    import uuid as _uuid
    log = AuditLog(
        id=str(_uuid.uuid4()),
        user_id=admin.id,
        action="security_alert_acknowledged",
        resource_type="security_alert",
        resource_id=alert_id,
        extra={"note": body.note[:500], "acknowledged_by": admin.email},
    )
    db.add(log)
    db.commit()
    return {"success": True, "alert_id": alert_id}


@router.post("/security/alerts/{alert_id}/lock-account")
async def lock_account_from_alert(
    alert_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin = _require_admin(credentials, db)
    user = None
    if alert_id.startswith("fin_"):
        job = db.query(AgentJob).filter(AgentJob.id == alert_id[4:]).first()
        if job:
            ws = db.query(Workspace).filter(Workspace.id == job.workspace_id).first()
            org = db.query(Organization).filter(Organization.id == ws.organization_id).first() if ws else None
            user = db.query(User).filter(User.id == org.owner_id).first() if org else None
    else:
        entry = db.query(AuditLog).filter(AuditLog.id == alert_id).first()
        if entry and entry.user_id:
            user = db.query(User).filter(User.id == entry.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Client not resolved from alert")

    user.is_active = False
    db.commit()

    import uuid as _uuid
    db.add(AuditLog(
        id=str(_uuid.uuid4()),
        user_id=admin.id,
        action="account_locked",
        resource_type="user",
        resource_id=user.id,
        extra={"reason": f"Locked from security alert {alert_id}", "locked_by": admin.email},
    ))
    db.commit()
    return {"success": True, "client_id": user.id, "client_email": user.email}


# ─── Settings & Governance ────────────────────────────────────────────────────

@router.get("/settings")
async def get_settings(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)

    from app.agents.agent_registry import (
        AGENTS_MAY_NOT_SPEND,
        AGENTS_MAY_NOT_SCALE_PAID,
        AGENTS_MAY_NOT_SIGN_AGREEMENTS,
    )

    env = os.getenv("ENVIRONMENT", "production")

    return {
        "financial_constraints": {
            "agents_may_not_spend": AGENTS_MAY_NOT_SPEND,
            "agents_may_not_scale_paid": AGENTS_MAY_NOT_SCALE_PAID,
            "agents_may_not_sign_agreements": AGENTS_MAY_NOT_SIGN_AGREEMENTS,
            "note": "Hard-coded safety rules. Cannot be overridden via API or admin portal.",
        },
        "environment": {
            "name": env,
            "is_production": env == "production",
            "docs_exposed": env != "production",
            "server_header_suppressed": True,
            "csrf_enabled": os.getenv("TESTING", "0") != "1",
            "inline_worker_disabled": os.getenv("DISABLE_INLINE_WORKER", "0") == "1",
        },
        "rate_limits": {
            "global": "200/min",
            "login": "10/min",
            "media_generation": "5/min",
            "billing": "20/min",
        },
        "hitl_levels": {
            "0": {"model": "Fast / lightweight", "trigger": "Low-stakes, high-volume"},
            "1": {"model": "Standard", "trigger": "Standard agents"},
            "2": {"model": "Standard", "trigger": "Standard — elevated context"},
            "3": {"model": "Advanced", "trigger": "Spend / scale approval required — job held pending_approval"},
        },
        "credit_rules": {
            "video_credit_interval_seconds": 15,
            "plan_credits": {"starter": 50, "growth": 150, "business": 300},
            "plan_max_video_seconds": {"starter": 30, "growth": 90, "business": 90},
            "agent_task_credit_range": "1–5 credits per task",
        },
        "security_rules": {
            "injection_guard_active": True,
            "financial_output_scanner_active": True,
            "suspicious_path_detection_active": True,
            "tech_stack_opacity_enforced": True,
            "openapi_docs_in_production": False,
        },
        "provider_status": {
            "heygen_configured": bool(os.getenv("HEYGEN_API_KEY")),
            "stripe_configured": bool(os.getenv("STRIPE_SECRET_KEY")),
            "sqs_configured": bool(os.getenv("SQS_JOBS_QUEUE_URL")),
            "redis_configured": bool(os.getenv("REDIS_URL")),
            "sentry_configured": bool(os.getenv("SENTRY_DSN")),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        },
        "admin_config": {
            "admin_email_configured": bool(os.getenv("ADMIN_EMAIL")),
            "multi_admin_supported": True,
            "disable_inline_worker": os.getenv("DISABLE_INLINE_WORKER", "0") == "1",
        },
    }


# ─── Audit Logs ───────────────────────────────────────────────────────────────

@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Query(None),
    action: str = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """List audit log entries. Admin only."""
    _require_admin(credentials, db)

    q = db.query(AuditLog)

    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if from_date:
        try:
            from datetime import datetime as _dt
            q = q.filter(AuditLog.created_at >= _dt.fromisoformat(from_date))
        except ValueError:
            pass
    if to_date:
        try:
            from datetime import datetime as _dt
            q = q.filter(AuditLog.created_at <= _dt.fromisoformat(to_date))
        except ValueError:
            pass

    total = q.count()
    logs = q.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "details": log.extra,
            }
            for log in logs
        ],
    }


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------

class AnnouncementCreate(BaseModel):
    title: str = Field(..., max_length=200)
    body: str
    affects: Optional[str] = None
    type: str = "info"
    target_tier: str = "all"
    show_as: str = "banner"
    expires_at: Optional[str] = None


@router.get("/announcements")
async def list_announcements(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    rows = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    return [
        {
            "id": a.id, "title": a.title, "body": a.body, "affects": a.affects,
            "type": a.type, "target_tier": a.target_tier, "active": a.active,
            "show_as": a.show_as,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "expires_at": a.expires_at.isoformat() if a.expires_at else None,
            "created_by": a.created_by,
        }
        for a in rows
    ]


@router.post("/announcements", status_code=201)
async def create_announcement(
    payload: AnnouncementCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin = _require_admin(credentials, db)
    expires = None
    if payload.expires_at:
        try:
            expires = datetime.fromisoformat(payload.expires_at)
        except ValueError:
            pass
    a = Announcement(
        id=str(uuid.uuid4()),
        title=payload.title,
        body=payload.body,
        affects=payload.affects,
        type=payload.type,
        target_tier=payload.target_tier,
        show_as=payload.show_as,
        active=True,
        created_at=datetime.utcnow(),
        expires_at=expires,
        created_by=admin.email,
    )
    db.add(a)
    db.commit()
    return {"id": a.id, "created": True}


@router.put("/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    payload: AnnouncementCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Announcement not found")
    a.title = payload.title
    a.body = payload.body
    a.affects = payload.affects
    a.type = payload.type
    a.target_tier = payload.target_tier
    a.show_as = payload.show_as
    if payload.expires_at:
        try:
            a.expires_at = datetime.fromisoformat(payload.expires_at)
        except ValueError:
            pass
    db.commit()
    return {"updated": True}


@router.patch("/announcements/{announcement_id}/toggle")
async def toggle_announcement(
    announcement_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Announcement not found")
    a.active = not a.active
    db.commit()
    return {"active": a.active}


@router.delete("/announcements/{announcement_id}", status_code=204)
async def delete_announcement(
    announcement_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(a)
    db.commit()


# ---------------------------------------------------------------------------
# Agent Changelog
# ---------------------------------------------------------------------------

class ChangelogCreate(BaseModel):
    agent_id: str
    agent_name: str
    version: str
    summary: str = Field(..., max_length=300)
    changes: Optional[List[str]] = []
    affects: Optional[str] = None
    release_date: Optional[str] = None


@router.get("/agent-changelogs")
async def list_changelogs(
    agent_id: Optional[str] = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    q = db.query(AgentChangelog)
    if agent_id:
        q = q.filter(AgentChangelog.agent_id == agent_id)
    rows = q.order_by(AgentChangelog.release_date.desc()).all()
    return [_fmt_changelog(c) for c in rows]


@router.post("/agent-changelogs", status_code=201)
async def create_changelog(
    payload: ChangelogCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin = _require_admin(credentials, db)
    release = datetime.utcnow()
    if payload.release_date:
        try:
            release = datetime.fromisoformat(payload.release_date)
        except ValueError:
            pass
    c = AgentChangelog(
        id=str(uuid.uuid4()),
        agent_id=payload.agent_id,
        agent_name=payload.agent_name,
        version=payload.version,
        summary=payload.summary,
        changes=payload.changes or [],
        affects=payload.affects,
        release_date=release,
        created_by=admin.email,
    )
    db.add(c)
    db.commit()
    return {"id": c.id, "created": True}


@router.delete("/agent-changelogs/{changelog_id}", status_code=204)
async def delete_changelog(
    changelog_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    c = db.query(AgentChangelog).filter(AgentChangelog.id == changelog_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Changelog not found")
    db.delete(c)
    db.commit()


def _fmt_changelog(c: AgentChangelog) -> dict:
    return {
        "id": c.id, "agent_id": c.agent_id, "agent_name": c.agent_name,
        "version": c.version, "summary": c.summary, "changes": c.changes or [],
        "affects": c.affects,
        "release_date": c.release_date.isoformat() if c.release_date else None,
        "created_by": c.created_by,
    }


# ---------------------------------------------------------------------------
# System Status
# ---------------------------------------------------------------------------

DEFAULT_COMPONENTS = [
    {"name": "Agent Execution", "status": "operational", "description": ""},
    {"name": "Media Generation", "status": "operational", "description": ""},
    {"name": "API",             "status": "operational", "description": ""},
    {"name": "Billing",         "status": "operational", "description": ""},
    {"name": "Reports",         "status": "operational", "description": ""},
    {"name": "File Storage",    "status": "operational", "description": ""},
]


class StatusUpdate(BaseModel):
    overall: str
    message: Optional[str] = None
    components: Optional[List[dict]] = None


@router.get("/system-status")
async def get_system_status(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _require_admin(credentials, db)
    return _fetch_status(db)


@router.put("/system-status")
async def update_system_status(
    payload: StatusUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin = _require_admin(credentials, db)
    row = db.query(SystemStatus).filter(SystemStatus.id == 1).first()
    if not row:
        row = SystemStatus(id=1, overall="operational", updated_at=datetime.utcnow())
        db.add(row)
    row.overall = payload.overall
    row.message = payload.message
    if payload.components is not None:
        row.components = payload.components
    row.updated_at = datetime.utcnow()
    row.updated_by = admin.email
    db.commit()
    return _fetch_status(db)


def _fetch_status(db: Session) -> dict:
    row = db.query(SystemStatus).filter(SystemStatus.id == 1).first()
    if not row:
        return {
            "overall": "operational", "message": None,
            "components": DEFAULT_COMPONENTS, "updated_at": None, "updated_by": None,
        }
    return {
        "overall": row.overall,
        "message": row.message,
        "components": row.components or DEFAULT_COMPONENTS,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        "updated_by": row.updated_by,
    }
