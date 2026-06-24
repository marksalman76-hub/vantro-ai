"""
Public API v1 — programmatic agent access via API keys.

Authentication: Bearer token = raw API key (prefix "vtro_").
Keys are SHA-256 hashed before storage; raw key shown only once at creation.

Endpoints:
  POST /api/v1/keys              — create API key (JWT auth required)
  GET  /api/v1/keys              — list workspace keys (JWT auth required)
  DELETE /api/v1/keys/{key_id}   — revoke key (JWT auth required)
  GET  /api/v1/agents            — list available agents (API key auth)
  POST /api/v1/agents/{id}/run   — run agent (API key auth)
  GET  /api/v1/jobs/{job_id}     — poll job (API key auth)
"""
import hashlib
import json
import logging
import os
import secrets
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.config import get_config
from app.database import SessionLocal
from app.limiter import limiter
from app.models import Organization, User
from app.models.agent_system import AgentJob, APIKey
from app.models.workspace import CreditsAccount, Workspace

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["api-v1"])
security = HTTPBearer(auto_error=False)

KEY_PREFIX = "vtro_"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _jwt_user(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _api_key_workspace(credentials: HTTPAuthorizationCredentials, db: Session) -> tuple[APIKey, Workspace]:
    """Authenticate via API key and return (key_record, workspace)."""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    raw = credentials.credentials
    if not raw.startswith(KEY_PREFIX):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    key_hash = _hash_key(raw)
    record = db.query(APIKey).filter(APIKey.key_hash == key_hash, APIKey.is_active == True).first()
    if not record:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    if record.expires_at and record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API key expired")

    ws = db.query(Workspace).filter(Workspace.id == record.workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    record.last_used_at = datetime.utcnow()
    db.commit()
    return record, ws


def _ws_for_user(user: User, db: Session) -> Workspace:
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        raise HTTPException(status_code=400, detail="No organization found")
    ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found")
    return ws


# ── Key management (JWT-authenticated) ────────────────────────────────────────

class CreateKeyRequest(BaseModel):
    name: str = "API Key"


@router.post("/keys")
@limiter.limit("5/minute")
async def create_api_key(
    request: Request,
    body: CreateKeyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Create a new API key for this workspace. Raw key returned once — store it securely."""
    user = _jwt_user(credentials, db)
    ws = _ws_for_user(user, db)

    # Max 5 active keys per workspace
    active_count = db.query(APIKey).filter(APIKey.workspace_id == ws.id, APIKey.is_active == True).count()
    if active_count >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 active API keys per workspace")

    raw_key = KEY_PREFIX + secrets.token_urlsafe(32)
    key_hash = _hash_key(raw_key)
    key_prefix = raw_key[:12]  # "vtro_" + 7 chars

    record = APIKey(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=body.name[:100],
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()

    logger.info("API key created for workspace %s by user %s", ws.id, user.id)
    return {
        "key_id": record.id,
        "key": raw_key,  # ONLY time raw key is returned
        "prefix": key_prefix,
        "name": record.name,
        "warning": "Store this key securely — it will not be shown again.",
    }


@router.get("/keys")
async def list_api_keys(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _jwt_user(credentials, db)
    ws = _ws_for_user(user, db)
    keys = db.query(APIKey).filter(APIKey.workspace_id == ws.id).all()
    return {"keys": [
        {
            "key_id": k.id,
            "prefix": k.key_prefix,
            "name": k.name,
            "is_active": k.is_active,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "created_at": k.created_at.isoformat() if k.created_at else None,
        }
        for k in keys
    ]}


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _jwt_user(credentials, db)
    ws = _ws_for_user(user, db)
    record = db.query(APIKey).filter(APIKey.id == key_id, APIKey.workspace_id == ws.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="API key not found")
    record.is_active = False
    db.commit()
    return {"revoked": key_id}


# ── Agent access (API key authenticated) ──────────────────────────────────────

@router.get("/agents")
@limiter.limit("60/minute")
async def v1_list_agents(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """List all agents available to this workspace."""
    from app.agents.agent_registry import AGENT_CATALOGUE
    _, ws = _api_key_workspace(credentials, db)
    return {
        "agents": [
            {"id": aid, "name": meta["name"], "category": meta["category"],
             "credit_estimate": meta["credit_estimate"], "hitl_level": meta["hitl_default"]}
            for aid, meta in AGENT_CATALOGUE.items()
        ]
    }


class V1RunRequest(BaseModel):
    prompt: str
    context: dict = {}
    output_language: str = ""


@router.post("/agents/{agent_id}/run")
@limiter.limit("20/minute")
async def v1_run_agent(
    agent_id: str,
    request: Request,
    body: V1RunRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Submit an agent job via API key. Returns job_id for polling."""
    from app.agents.agent_registry import AGENT_CATALOGUE, normalize_agent_id, get_agent_hitl

    key_record, ws = _api_key_workspace(credentials, db)
    norm_id = normalize_agent_id(agent_id)
    if norm_id not in AGENT_CATALOGUE:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    meta = AGENT_CATALOGUE[norm_id]
    credit_cost = meta["credit_estimate"]
    hitl = get_agent_hitl(norm_id)

    cred = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == ws.id).with_for_update().first()
    remaining = (cred.total_credits - cred.used_credits) if cred else 0
    if remaining < credit_cost:
        raise HTTPException(status_code=402, detail=f"Insufficient credits. Need {credit_cost}, have {remaining}.")

    if cred and hitl != "HITL-3":
        cred.used_credits += credit_cost
        cred.updated_at = datetime.utcnow()

    ctx = body.context
    if body.output_language:
        ctx["output_language"] = body.output_language

    now = datetime.utcnow()
    job = AgentJob(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        agent_id=norm_id,
        agent_name=meta["name"],
        status="pending" if hitl != "HITL-3" else "pending_approval",
        hitl_level=hitl,
        input_data=json.dumps({"prompt": body.prompt[:10_000], "context": ctx, "_api_key_id": key_record.id}),
        credits_used=credit_cost,
        output_language=body.output_language or None,
        created_at=now,
        updated_at=now,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "agent_id": norm_id,
        "status": job.status,
        "credit_estimate": credit_cost,
    }


@router.get("/jobs/{job_id}")
@limiter.limit("60/minute")
async def v1_get_job(
    job_id: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Poll job status and retrieve output when completed."""
    _, ws = _api_key_workspace(credentials, db)
    job = db.query(AgentJob).filter(AgentJob.id == job_id, AgentJob.workspace_id == ws.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    output = None
    if job.status in ("completed", "pending_financial_review") and job.output_data:
        output = job.output_data

    return {
        "job_id": job.id,
        "agent_id": job.agent_id,
        "status": job.status,
        "output": output,
        "credits_used": job.credits_used,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
