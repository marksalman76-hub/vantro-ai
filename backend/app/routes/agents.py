"""
Client-facing Agents API
- GET  /api/agents            — list agents available to this workspace (package-gated)
- GET  /api/agents/all        — list all 27 agents (locked/unlocked metadata) for display
- POST /api/agents/{id}/run   — submit an agent job (HITL-3 budget gates enforced externally)
- GET  /api/agents/jobs       — list this workspace's agent job history
- POST /api/packages/download — generate an OTC code for a package download (one-time)
- POST /api/packages/redeem   — redeem an OTC code (one-time use, marks as used)
"""
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Organization
from app.models.workspace import Workspace, CreditsAccount
from app.models.agent_system import AgentJob, PackageDownload
from app.agents.agent_registry import (
    AGENT_CATALOGUE,
    INTERNAL_AGENTS,
    PACKAGE_AGENTS,
    TIER_ORDER,
    agents_for_package,
    get_agent,
    normalize_agent_id,
    STARTER,
)

router = APIRouter(tags=["agents"])
security = HTTPBearer(auto_error=False)

PLAN_CREDITS = {"starter": 60, "growth": 200, "business": 300, "enterprise": 9999}


# ---------------------------------------------------------------------------
# DB / auth helpers
# ---------------------------------------------------------------------------

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


def _workspace_tier(user: User, db: Session) -> tuple[str, Workspace | None, CreditsAccount | None]:
    """Return (tier, workspace, credits_account) for the user's first org/workspace."""
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        return STARTER, None, None
    ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    if not ws:
        return STARTER, None, None
    cred = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == ws.id).first()
    total = cred.total_credits if cred else 0

    if total >= PLAN_CREDITS["business"]:
        # enterprise marker: credit total well above business threshold
        tier = "enterprise" if total >= 500 else "business"
    elif total >= PLAN_CREDITS["growth"]:
        tier = "growth"
    elif total >= PLAN_CREDITS["starter"]:
        tier = "starter"
    else:
        tier = "free"
    return tier, ws, cred


def _serialize_agent(agent_id: str, unlocked: bool) -> dict:
    meta = AGENT_CATALOGUE[agent_id]
    return {
        "id": agent_id,
        "name": meta["name"],
        "category": meta["category"],
        "role": meta["role"],
        "architecture": meta["architecture"],
        "hitl_level": meta["hitl_default"],
        "min_package": meta["min_package"],
        "credit_estimate": meta["credit_estimate"],
        "capabilities": meta.get("capabilities", []),
        "unlocked": unlocked,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/api/agents/all")
async def list_all_agents(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return all 27 agents with unlocked=True/False based on workspace tier."""
    user = _get_user(credentials, db)
    tier, _, _ = _workspace_tier(user, db)
    available = set(agents_for_package(tier))

    return {
        "tier": tier,
        "total": len(AGENT_CATALOGUE),
        "agents": [
            _serialize_agent(aid, aid in available)
            for aid in AGENT_CATALOGUE
        ],
    }


@router.get("/api/agents")
async def list_available_agents(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return only the agents unlocked for this workspace's tier."""
    user = _get_user(credentials, db)
    tier, _, _ = _workspace_tier(user, db)
    available_ids = agents_for_package(tier)

    return {
        "tier": tier,
        "total": len(available_ids),
        "agents": [_serialize_agent(aid, True) for aid in available_ids],
    }


class AgentRunRequest(BaseModel):
    prompt: str
    context: dict = {}


@router.post("/api/agents/{agent_id}/run")
async def run_agent(
    agent_id: str,
    body: AgentRunRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Submit an agent job.
    HITL-3 agents (ads, ugc, finance, workflow, head) are queued as 'pending_approval'
    and require admin approval before execution.
    """
    user = _get_user(credentials, db)
    tier, ws, cred = _workspace_tier(user, db)

    norm_id = normalize_agent_id(agent_id)
    if norm_id not in AGENT_CATALOGUE:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    available = set(agents_for_package(tier))
    if norm_id not in available:
        raise HTTPException(
            status_code=403,
            detail=f"Agent '{norm_id}' requires a higher plan. Your current tier: {tier}",
        )

    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found for this account")

    meta = AGENT_CATALOGUE[norm_id]
    credit_cost = meta["credit_estimate"]
    hitl = meta["hitl_default"]

    remaining = (cred.total_credits - cred.used_credits) if cred else 0
    if remaining < credit_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Need {credit_cost}, have {remaining}.",
        )

    # HITL-3 jobs go into pending_approval — must not auto-execute spend
    status = "pending_approval" if hitl == "HITL-3" else "pending"

    import json as _json
    now = datetime.utcnow()
    job = AgentJob(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        agent_id=norm_id,
        agent_name=meta["name"],
        status=status,
        hitl_level=hitl,
        input_data=_json.dumps({"prompt": body.prompt[:10_000], "context": body.context}),
        credits_used=0,  # deducted on completion by worker
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
        "status": status,
        "hitl_level": hitl,
        "credit_estimate": credit_cost,
        "message": (
            "Job queued for admin approval (HITL-3 spend gate)"
            if status == "pending_approval"
            else "Job queued for processing"
        ),
    }


@router.get("/api/agents/jobs/{job_id}")
async def get_agent_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Poll a specific job for status and output."""
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    job = db.query(AgentJob).filter(AgentJob.id == job_id, AgentJob.workspace_id == ws.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Strip provider metadata comment from output before returning to client
    output = job.output_data or ""
    if output.startswith("<!-- provider:"):
        output = output.split(" -->\n", 1)[-1]

    return {
        "job_id": job.id,
        "agent_id": job.agent_id,
        "agent_name": job.agent_name,
        "status": job.status,
        "hitl_level": job.hitl_level,
        "credits_used": job.credits_used,
        "output": output if job.status == "completed" else None,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


@router.get("/api/agents/jobs")
async def list_agent_jobs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        return {"total": 0, "jobs": []}

    jobs = (
        db.query(AgentJob)
        .filter(AgentJob.workspace_id == ws.id)
        .order_by(AgentJob.created_at.desc())
        .limit(100)
        .all()
    )
    return {
        "total": len(jobs),
        "jobs": [
            {
                "id": j.id,
                "agent_id": j.agent_id,
                "agent_name": j.agent_name,
                "status": j.status,
                "hitl_level": j.hitl_level,
                "credits_used": j.credits_used,
                "error_message": j.error_message,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            }
            for j in jobs
        ],
    }


# ---------------------------------------------------------------------------
# Package download OTC
# ---------------------------------------------------------------------------

class PackageDownloadRequest(BaseModel):
    package_name: str


class OtcRedeemRequest(BaseModel):
    otc_code: str


@router.post("/api/packages/download")
async def generate_package_download(
    body: PackageDownloadRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Generate a unique OTC for a package download.
    Each workspace may only download each package once.
    """
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found for this account")

    package = body.package_name.strip().lower()
    if not package:
        raise HTTPException(status_code=400, detail="package_name is required")

    # Enforce one-download-per-package-per-workspace
    existing = (
        db.query(PackageDownload)
        .filter(
            PackageDownload.workspace_id == ws.id,
            PackageDownload.package_name == package,
        )
        .first()
    )
    if existing:
        if existing.is_used:
            raise HTTPException(
                status_code=409,
                detail=f"Package '{package}' has already been downloaded by this account. Each package may only be downloaded once.",
            )
        # OTC exists but not yet used — return the existing code
        return {
            "otc_code": existing.otc_code,
            "package_name": existing.package_name,
            "expires_at": existing.expires_at.isoformat() if existing.expires_at else None,
            "is_used": existing.is_used,
            "message": "Existing unused OTC returned. Download it before it expires.",
        }

    otc = str(uuid.uuid4())
    now = datetime.utcnow()
    dl = PackageDownload(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        package_name=package,
        otc_code=otc,
        is_used=False,
        expires_at=now + timedelta(hours=24),
        ip_address=request.client.host if request.client else None,
        created_at=now,
        updated_at=now,
    )
    db.add(dl)
    db.commit()
    db.refresh(dl)

    return {
        "otc_code": dl.otc_code,
        "package_name": dl.package_name,
        "expires_at": dl.expires_at.isoformat() if dl.expires_at else None,
        "is_used": False,
        "message": "OTC generated. Use this code once to download the package. Expires in 24 hours.",
    }


@router.post("/api/packages/redeem")
async def redeem_package_download(
    body: OtcRedeemRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Validate and redeem an OTC. Can only be used once.
    Returns the package download payload on success.
    """
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found for this account")

    code = body.otc_code.strip()
    dl = db.query(PackageDownload).filter(PackageDownload.otc_code == code).first()
    if not dl:
        raise HTTPException(status_code=404, detail="Invalid OTC code")

    if dl.workspace_id != ws.id:
        raise HTTPException(status_code=403, detail="This OTC belongs to a different account")

    if dl.is_used:
        raise HTTPException(
            status_code=409,
            detail="This OTC has already been used. Each package may only be downloaded once.",
        )

    if dl.expires_at and datetime.utcnow() > dl.expires_at:
        raise HTTPException(status_code=410, detail="This OTC has expired. Contact support.")

    now = datetime.utcnow()
    dl.is_used = True
    dl.used_at = now
    dl.updated_at = now
    db.commit()

    return {
        "success": True,
        "package_name": dl.package_name,
        "redeemed_at": now.isoformat(),
        "message": f"Package '{dl.package_name}' download authorized. This OTC is now invalidated.",
    }
