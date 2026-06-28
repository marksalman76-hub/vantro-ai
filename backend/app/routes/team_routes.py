"""
Team Runs API
- POST /api/agents/team/run        — submit a multi-agent team run
- GET  /api/agents/team/{id}/status — poll team run status and all child jobs
"""
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.auth import verify_token
from app.database import SessionLocal
from app.limiter import limiter
from app.models import User, Organization
from app.models.workspace import Workspace, CreditsAccount
from app.models.agent_system import AgentJob, TeamRun
from app.agents.agent_registry import (
    AGENT_CATALOGUE,
    AGENT_GOVERNANCE,
    PLATFORM_TEAM_TEMPLATES,
    agents_for_package,
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


def _workspace_tier(user: User, db: Session) -> tuple[str, Optional[Workspace], Optional[CreditsAccount]]:
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
        tier = "enterprise" if total >= 500 else "business"
    elif total >= PLAN_CREDITS["growth"]:
        tier = "growth"
    elif total >= PLAN_CREDITS["starter"]:
        tier = "starter"
    else:
        tier = "free"
    return tier, ws, cred


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class TeamRunRequest(BaseModel):
    objective: str
    lead_agent_id: str
    agent_ids: list[str]
    team_template_id: Optional[str] = None
    business_context: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/api/agents/team/run")
@limiter.limit("10/minute")
async def create_team_run(
    request: Request,
    body: TeamRunRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Submit a multi-agent team run.
    - Min 2, max 7 agents
    - lead_agent_id must have lead_agent_allowed: True in AGENT_GOVERNANCE
    - lead_agent_id must be in agent_ids
    - All agents must be available on the workspace's package tier
    - Credits are deducted upfront unless any agent requires HITL-3 approval
    """
    user = _get_user(credentials, db)
    tier, ws, cred = _workspace_tier(user, db)

    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found for this account")

    # Normalize all agent IDs
    normalized_agent_ids = [normalize_agent_id(aid) for aid in body.agent_ids]
    normalized_lead_id = normalize_agent_id(body.lead_agent_id)

    # Validation 1: agent count
    if len(normalized_agent_ids) < 2:
        raise HTTPException(status_code=400, detail="A team run requires at least 2 agents")
    if len(normalized_agent_ids) > 7:
        raise HTTPException(status_code=400, detail="A team run may not exceed 7 agents")

    # Validation 2: all agent_ids must exist in AGENT_CATALOGUE
    for aid in normalized_agent_ids:
        if aid not in AGENT_CATALOGUE:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {aid}")

    # Validation 3: lead_agent_id must exist and have lead_agent_allowed: True
    if normalized_lead_id not in AGENT_CATALOGUE:
        raise HTTPException(status_code=400, detail=f"Unknown lead agent: {normalized_lead_id}")
    lead_governance = AGENT_GOVERNANCE.get(normalized_lead_id, {})
    if not lead_governance.get("lead_agent_allowed", False):
        raise HTTPException(
            status_code=400,
            detail=f"Agent '{normalized_lead_id}' is not permitted to act as a lead agent",
        )

    # Validation 4: lead_agent_id must be in agent_ids
    if normalized_lead_id not in normalized_agent_ids:
        raise HTTPException(
            status_code=400,
            detail="lead_agent_id must be included in agent_ids",
        )

    # Validation 5: all agents must be available on the workspace tier
    available = set(agents_for_package(tier))
    for aid in normalized_agent_ids:
        if aid not in available:
            raise HTTPException(
                status_code=403,
                detail=f"Agent '{aid}' requires a higher plan. Your current tier: {tier}",
            )

    # Validation 6: team_template_id must exist if provided
    if body.team_template_id is not None:
        template_ids = {t["id"] for t in PLATFORM_TEAM_TEMPLATES}
        if body.team_template_id not in template_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown team template: {body.team_template_id}",
            )

    # Validation 7: workspace must have enough credits
    total_credits_estimate = sum(
        AGENT_CATALOGUE[aid]["credit_estimate"] for aid in normalized_agent_ids
    )
    # Re-acquire with row-level lock to prevent concurrent overdraw (TOCTOU guard)
    cred = (
        db.query(CreditsAccount)
        .filter(CreditsAccount.workspace_id == ws.id)
        .with_for_update()
        .first()
    )
    remaining = (cred.total_credits - cred.used_credits) if cred else 0
    if remaining < total_credits_estimate:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Need {total_credits_estimate}, have {remaining}.",
        )

    # Determine if HITL-3 approval is required (any agent with hitl_default == "HITL-3")
    requires_hitl3_approval = any(
        AGENT_CATALOGUE[aid]["hitl_default"] == "HITL-3"
        for aid in normalized_agent_ids
    )

    now = datetime.utcnow()

    # Create TeamRun row
    team_run = TeamRun(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        lead_agent_id=normalized_lead_id,
        agent_ids=json.dumps(normalized_agent_ids),
        objective=body.objective[:10_000],
        status="pending",
        credits_used=total_credits_estimate,
        requires_hitl3_approval=requires_hitl3_approval,
        created_at=now,
    )
    db.add(team_run)

    # Create AgentJob rows: lead first, then the rest
    ordered_agent_ids = [normalized_lead_id] + [
        aid for aid in normalized_agent_ids if aid != normalized_lead_id
    ]

    job_status = "pending_approval" if requires_hitl3_approval else "pending"
    jobs_created = []
    lead_job_id = None

    for aid in ordered_agent_ids:
        meta = AGENT_CATALOGUE[aid]
        is_lead = (aid == normalized_lead_id)
        role = "lead" if is_lead else "supporting"

        input_payload = {
            "prompt": body.objective,
            "context": {
                "business_context": body.business_context or "",
                "team_run_id": team_run.id,
                "role": role,
            },
        }

        job = AgentJob(
            id=str(uuid.uuid4()),
            workspace_id=ws.id,
            agent_id=aid,
            agent_name=meta["name"],
            status=job_status,
            hitl_level=meta["hitl_default"],
            input_data=json.dumps(input_payload),
            credits_used=meta["credit_estimate"],
            team_run_id=team_run.id,
            created_at=now,
            updated_at=now,
        )
        db.add(job)
        jobs_created.append({
            "job_id": job.id,
            "agent_id": aid,
            "agent_name": meta["name"],
            "status": job_status,
        })

        if is_lead:
            lead_job_id = job.id

    # Deduct credits upfront only if no HITL-3 approval required
    if not requires_hitl3_approval and cred:
        cred.used_credits = cred.used_credits + total_credits_estimate
        cred.updated_at = now

    db.commit()

    return {
        "team_run_id": team_run.id,
        "lead_job_id": lead_job_id,
        "jobs": jobs_created,
        "credits_estimate": total_credits_estimate,
        "requires_approval": requires_hitl3_approval,
        "message": "Team run queued for processing",
    }


@router.get("/api/agents/team/{team_run_id}/status")
@limiter.limit("30/minute")
async def get_team_run_status(
    team_run_id: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Poll a team run for status and all child job outputs."""
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)

    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    # Load TeamRun — always filter by workspace_id to prevent cross-workspace access
    team_run = (
        db.query(TeamRun)
        .filter(TeamRun.id == team_run_id, TeamRun.workspace_id == ws.id)
        .first()
    )
    if not team_run:
        raise HTTPException(status_code=404, detail="Team run not found")

    # Load all AgentJobs for this team run
    jobs = (
        db.query(AgentJob)
        .filter(
            AgentJob.team_run_id == team_run_id,
            AgentJob.workspace_id == ws.id,
        )
        .order_by(AgentJob.created_at.asc())
        .all()
    )

    def _serialize_job(j: AgentJob) -> dict:
        return {
            "job_id": j.id,
            "agent_id": j.agent_id,
            "agent_name": j.agent_name,
            "status": j.status,
            "credits_used": j.credits_used,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "output": j.output_data if j.status == "completed" else None,
        }

    lead_job_data = None
    supporting_job_data = []

    for j in jobs:
        if j.agent_id == team_run.lead_agent_id and lead_job_data is None:
            lead_job_data = _serialize_job(j)
        else:
            supporting_job_data.append(_serialize_job(j))

    output = None
    if team_run.output:
        try:
            output = json.loads(team_run.output)
        except Exception:
            output = team_run.output

    return {
        "team_run_id": team_run.id,
        "status": team_run.status,
        "lead_job": lead_job_data,
        "supporting_jobs": supporting_job_data,
        "output": output,
        "credits_used": team_run.credits_used,
        "requires_approval": team_run.requires_hitl3_approval,
    }
