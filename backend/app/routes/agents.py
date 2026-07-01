"""
Client-facing Agents API
- GET  /api/agents            — list agents available to this workspace (package-gated)
- GET  /api/agents/all        — list all 27 agents (locked/unlocked metadata) for display
- POST /api/agents/{id}/run   — submit an agent job (HITL-3 budget gates enforced externally)
- POST /api/agents/{id}/stream — stream LLM output as SSE (HITL-3 blocked, fire-and-forget)
- GET  /api/agents/jobs       — list this workspace's agent job history
- POST /api/packages/download — generate an OTC code for a package download (one-time)
- POST /api/packages/redeem   — redeem an OTC code (one-time use, marks as used)
"""
import json
import os
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.limiter import limiter
from app.models import User, Organization
from app.services import cache_service
from app.models.workspace import Workspace, CreditsAccount
from app.models.agent_system import AgentJob, PackageDownload
from app.services.email_service import send_approval_needed
from app.agents.agent_registry import (
    AGENT_CATALOGUE,
    AGENT_GOVERNANCE,
    AGENTS_MAY_NOT_SPEND,
    AGENTS_MAY_NOT_SCALE_PAID,
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


def _is_admin(user: User) -> bool:
    """Return True if the user has admin privileges (DB flag or ADMIN_EMAIL env match).

    Single source of truth for admin detection. Use this helper everywhere —
    do NOT duplicate the env-var check inline in route handlers.
    """
    admin_email = os.getenv("ADMIN_EMAIL", "")
    return bool(
        user.is_admin
        or (admin_email and user.email.lower() == admin_email.lower())
    )


def _workspace_tier(user: User, db: Session) -> tuple[str, Workspace | None, CreditsAccount | None]:
    """Return (tier, workspace, credits_account) for the user's first org/workspace.

    Admins always receive tier="enterprise" and cred=None (unlimited credits).
    cred=None is the canonical signal throughout this module that credit checks
    must be skipped — never introduce credit gates conditioned only on cred being None.
    """
    # Admin short-circuit: enterprise tier, no credit gate, workspace fetched for job records.
    if _is_admin(user):
        org = db.query(Organization).filter(Organization.owner_id == user.id).first()
        ws = (
            db.query(Workspace).filter(Workspace.organization_id == org.id).first()
            if org else None
        )
        return "enterprise", ws, None

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

    # _workspace_tier already returns enterprise for admins; defence-in-depth override.
    is_admin = _is_admin(user)
    if is_admin:
        tier = "enterprise"

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
    tier, ws, _ = _workspace_tier(user, db)

    # _workspace_tier already returns enterprise for admins; defence-in-depth override.
    is_admin = _is_admin(user)
    if is_admin:
        tier = "enterprise"

    workspace_id = ws.id if ws else user.id
    admin_suffix = ":admin" if is_admin else ""
    cache_key = f"agents:catalogue:{workspace_id}{admin_suffix}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=cached,
            headers={"Cache-Control": "max-age=300, private"},
        )

    available_ids = agents_for_package(tier)
    payload = {
        "tier": tier,
        "total": len(available_ids),
        "agents": [_serialize_agent(aid, True) for aid in available_ids],
    }
    cache_service.set(cache_key, payload, ttl=300)

    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=payload,
        headers={"Cache-Control": "max-age=300, private"},
    )


class AgentRunRequest(BaseModel):
    prompt: str
    context: dict = {}
    output_language: str = ""   # e.g. "Spanish", "French" — blank = English


@router.post("/api/agents/{agent_id}/run")
@limiter.limit("20/minute")
async def run_agent(
    agent_id: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Submit an agent job.
    HITL-3 agents (ads, ugc, finance, workflow, head) are queued as 'pending_approval'
    and require admin approval before execution.
    Accepts both JSON and multipart/form-data (with optional reference_files).
    """
    user = _get_user(credentials, db)
    tier, ws, cred = _workspace_tier(user, db)

    # _workspace_tier already returns enterprise for admins; defence-in-depth override.
    is_admin = _is_admin(user)
    if is_admin:
        tier = "enterprise"

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

    # Parse request body (JSON or multipart/form-data)
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        prompt = body.get("prompt", "")
        context = body.get("context", {})
        output_language = body.get("output_language", "")
        reference_files = []
    elif "multipart/form-data" in content_type:
        form = await request.form()
        prompt = form.get("prompt", "")
        context_str = form.get("context", "{}")
        try:
            context = json.loads(context_str) if isinstance(context_str, str) else context_str
        except:
            context = {}
        output_language = form.get("output_language", "")
        reference_files = form.getlist("reference_files")
    else:
        raise HTTPException(status_code=400, detail="Unsupported content type")

    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    meta = AGENT_CATALOGUE[norm_id]
    credit_cost = meta["credit_estimate"]
    hitl = meta["hitl_default"]

    # Admins bypass credit checks entirely
    if is_admin:
        cred = None
    else:
        # Re-acquire with row-level lock to prevent concurrent overdraw (TOCTOU guard)
        cred = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == ws.id).with_for_update().first()

        remaining = (cred.total_credits - cred.used_credits) if cred else 0
        if remaining < credit_cost:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient credits. Need {credit_cost}, have {remaining}.",
            )

    # ── Financial governance: submission-time gate ───────────────────────────
    # Platform policy (AGENTS_MAY_NOT_SPEND = True):
    # Agents may SUGGEST financial actions but never execute them.
    # The output scanner in agent_executor + agent_worker is the primary guard.
    #
    # At submission time we add one additional check: if the user's prompt
    # explicitly asks the agent to execute/authorise/commit a financial action
    # (e.g. "buy these ads", "spend $500 on Facebook"), we hold the job for
    # admin review before it even reaches the executor — defence-in-depth.
    from app.agents.agent_executor import scan_for_financial_actions
    prompt_violations = scan_for_financial_actions(prompt)
    if prompt_violations:
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "Financial execution language in prompt — held for review: agent=%s user=%s violations=%s",
            norm_id, user.email, prompt_violations,
        )

    # Financial execution intent → hold for admin review.
    # HITL-3 alone: submitter IS the approval authority → auto-approved.
    if prompt_violations:
        status = "pending_approval"
    elif hitl == "HITL-3":
        status = "approved"
    else:
        status = "pending"
    # ────────────────────────────────────────────────────────────────────────

    # Pre-commit credits at submission (not at completion) to prevent concurrent
    # submissions from racing past the guard.  The worker credits_used field on
    # the job still records what was actually consumed; the CreditsAccount is the
    # authoritative live balance.  If a job fails the worker restores the credits.
    if cred and status != "pending_approval":
        cred.used_credits = cred.used_credits + credit_cost
        cred.updated_at = datetime.utcnow()

    import json as _json
    _ctx = dict(context)
    if output_language:
        _ctx["output_language"] = output_language
    if is_admin:
        _ctx.update({
            "portal_mode": "admin",
            "actor_role": "owner_admin",
            "package_tier": "enterprise",
            "billing_mode": "owner_admin_unlimited",
            "credits_unlimited": True,
        })
    try:
        from app.runtime.creative_provider_routing import (
            is_creative_agent,
            resolve_creative_provider_route,
        )
        if is_creative_agent(norm_id):
            media_request = _ctx.get("media_request") if isinstance(_ctx.get("media_request"), dict) else {}
            route_media_type = media_request.get("media_type") or media_request.get("type") or _ctx.get("media_type") or "both"
            route_agent_id = agent_id if is_creative_agent(agent_id) else norm_id
            creative_provider_route = resolve_creative_provider_route(
                agent_id=route_agent_id,
                media_type=route_media_type,
                video_quality=media_request.get("video_quality") or _ctx.get("video_quality") or "",
                image_tier=media_request.get("image_tier") or _ctx.get("image_tier") or "",
                package_tier=tier,
                admin_override=is_admin,
                request_context=_ctx,
            )
            if not creative_provider_route.get("success"):
                reason = creative_provider_route.get("reason", "media_type_not_supported")
                raise HTTPException(status_code=400, detail=f"Creative route error: {reason}")
            _ctx["creative_provider_route"] = creative_provider_route
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent routing error: {type(e).__name__}")
    now = datetime.utcnow()
    job = AgentJob(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        agent_id=norm_id,
        agent_name=meta["name"],
        status=status,
        hitl_level=hitl,
        input_data=_json.dumps({"prompt": prompt[:10_000], "context": _ctx}),
        credits_used=credit_cost,
        output_language=output_language or None,
        created_at=now,
        updated_at=now,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Notify admin for HITL-3 jobs
    if status == "pending_approval":
        admin_email = os.getenv("ADMIN_EMAIL", "")
        if admin_email:
            try:
                send_approval_needed(admin_email, job.id, norm_id, user.email)
            except Exception:
                pass  # non-fatal

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

    output = job.output_data or ""

    steps_parsed = None
    try:
        if job.steps:
            steps_parsed = json.loads(job.steps)
    except Exception:
        pass

    return {
        "job_id": job.id,
        "agent_id": job.agent_id,
        "agent_name": job.agent_name,
        "status": job.status,
        "credits_used": job.credits_used,
        "output": output if job.status in ("completed", "pending_financial_review") else None,
        "financial_review_held": job.status == "pending_financial_review",
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "steps": steps_parsed,
        "rating": job.rating,
        "rating_comment": job.rating_comment,
        "output_language": job.output_language,
        "revision_of": job.revision_of,
    }


@router.get("/api/agents/jobs")
async def list_agent_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        return {"total": 0, "skip": skip, "limit": limit, "jobs": []}

    base_q = db.query(AgentJob).filter(AgentJob.workspace_id == ws.id)
    total = base_q.count()
    jobs = base_q.order_by(AgentJob.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "jobs": [
            {
                "id": j.id,
                "agent_id": j.agent_id,
                "agent_name": j.agent_name,
                "status": j.status,
                "credits_used": j.credits_used,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
                "rating": j.rating,
                "output_language": j.output_language,
                "revision_of": j.revision_of,
                "output_preview": (j.output_data or "")[:300] if j.status == "completed" else None,
                "output": j.output_data if j.status in ("completed", "pending_financial_review") else None,
            }
            for j in jobs
        ],
    }


@router.post("/api/agents/jobs/{job_id}/cancel")
async def cancel_agent_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Cancel a pending or pending_approval job and refund pre-committed credits."""
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    job = db.query(AgentJob).filter(AgentJob.id == job_id, AgentJob.workspace_id == ws.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in ("pending", "pending_approval"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel a job in '{job.status}' status")

    # Refund pre-committed credits for non-HITL-3 pending jobs
    if job.status == "pending":
        cred = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == ws.id).with_for_update().first()
        if cred:
            pre_committed = job.credits_used or 0
            if pre_committed > 0:
                cred.used_credits = max(0, cred.used_credits - pre_committed)
                cred.updated_at = datetime.utcnow()

    job.status = "cancelled"
    job.credits_used = 0
    job.updated_at = datetime.utcnow()
    db.commit()

    return {"job_id": job_id, "status": "cancelled"}


# ---------------------------------------------------------------------------
# SSE streaming route
# ---------------------------------------------------------------------------

class StreamRequest(BaseModel):
    prompt: str
    context: dict = {}


@router.post("/api/agents/{agent_id}/stream")
async def stream_agent(
    agent_id: str,
    body: StreamRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Stream LLM output for an agent as Server-Sent Events.

    - HITL-3 agents are blocked (too high-risk for the no-approval path).
    - Deducts 1 credit upfront; no refund on stream (fire-and-forget billing).
    - Does NOT create an AgentJob record.
    - Guards: FINANCIAL_CONSTRAINT_BLOCK + INJECTION_GUARD applied to system prompt.
    """
    from app.agents.agent_registry import get_agent_hitl, normalize_agent_id, agent_exists
    from app.agents.agent_prompts import get_agent_system_prompt
    from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, INJECTION_GUARD, HITL_MODEL_MAP

    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)

    is_admin = _is_admin(user)

    normalized = normalize_agent_id(agent_id)
    if not agent_exists(normalized):
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_id}")

    hitl = get_agent_hitl(normalized)
    if hitl == "HITL-3":
        raise HTTPException(
            status_code=403,
            detail="HITL-3 agents require owner approval and cannot be streamed directly.",
        )

    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found for this account")

    # Credit check and upfront deduction — skipped entirely for admins (unlimited credits).
    if not is_admin:
        cred = (
            db.query(CreditsAccount)
            .filter(CreditsAccount.workspace_id == ws.id)
            .with_for_update()
            .first()
        )
        remaining = (cred.total_credits - cred.used_credits) if cred else 0
        if remaining < 1:
            raise HTTPException(
                status_code=402,
                detail="Insufficient credits. Minimum 1 credit required to stream.",
            )

        if cred:
            cred.used_credits = cred.used_credits + 1
            cred.updated_at = datetime.utcnow()
            db.commit()

    # Build guarded prompt
    system_prompt = get_agent_system_prompt(normalized)
    guarded = FINANCIAL_CONSTRAINT_BLOCK + INJECTION_GUARD + system_prompt

    user_message = body.prompt
    if body.context:
        ctx_lines = "\n".join(f"{k}: {v}" for k, v in body.context.items() if v)
        if ctx_lines:
            user_message = f"Context:\n{ctx_lines}\n\n---\n\nTask:\n{user_message}"

    model = HITL_MODEL_MAP.get(hitl, "claude-sonnet-4-6")

    async def event_generator():
        # anthropic imported inside generator to avoid import errors when key is absent
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            yield f'data: {json.dumps({"type": "error", "message": "ANTHROPIC_API_KEY not configured"})}\n\n'
            return

        client = anthropic.Anthropic(api_key=api_key)
        yield f'data: {json.dumps({"type": "start", "agent_id": normalized})}\n\n'
        try:
            with client.messages.stream(
                model=model,
                max_tokens=4096,
                system=[{"type": "text", "text": guarded, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": user_message}],
                timeout=90,
            ) as stream:
                for text_chunk in stream.text_stream:
                    yield f'data: {json.dumps({"type": "chunk", "text": text_chunk})}\n\n'
            yield f'data: {json.dumps({"type": "done", "credits_used": 1})}\n\n'
        except Exception as e:
            logger.error("SSE stream error agent=%s: %s", normalized, e, exc_info=True)
            yield f'data: {json.dumps({"type": "error", "message": "An error occurred processing your request"})}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Output rating
# ---------------------------------------------------------------------------

class RateJobRequest(BaseModel):
    rating: int          # 1-5
    comment: str = ""


@router.post("/api/agents/jobs/{job_id}/rate")
@limiter.limit("30/minute")
async def rate_agent_job(
    job_id: str,
    request: Request,
    body: RateJobRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Client rates a completed job output 1-5 stars."""
    if body.rating < 1 or body.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    job = db.query(AgentJob).filter(AgentJob.id == job_id, AgentJob.workspace_id == ws.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in ("completed", "pending_financial_review"):
        raise HTTPException(status_code=400, detail="Can only rate completed jobs")

    job.rating = body.rating
    job.rating_comment = body.comment[:1000] if body.comment else None
    job.updated_at = datetime.utcnow()

    # Feed 5-star outputs into the few-shot example store (best-effort)
    if body.rating == 5 and job.output_data:
        try:
            from app.models.agent_system import AgentExample  # type: ignore
            clean_output = job.output_data.split(" -->\n", 1)[-1]
            input_parsed = json.loads(job.input_data or "{}")
            eg = AgentExample(
                id=str(uuid.uuid4()),
                agent_id=job.agent_id,
                input_text=(input_parsed.get("prompt", "") or "")[:2000],
                output_text=clean_output[:4000],
                created_at=datetime.utcnow(),
            )
            db.add(eg)
        except Exception:
            pass

    db.commit()
    return {"job_id": job_id, "rating": body.rating, "saved": True}


# ---------------------------------------------------------------------------
# Output revision
# ---------------------------------------------------------------------------

class ReviseJobRequest(BaseModel):
    revision_prompt: str    # what to change: "make it shorter and more direct"
    output_language: str = ""


@router.post("/api/agents/jobs/{job_id}/revise")
@limiter.limit("10/minute")
async def revise_agent_job(
    job_id: str,
    request: Request,
    body: ReviseJobRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Queue a revision of a completed job with a specific instruction.
    Creates a new AgentJob linked to the original via revision_of.
    Inherits the original agent, input, and context — only the revision_prompt differs.
    """
    user = _get_user(credentials, db)
    tier, ws, cred = _workspace_tier(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    is_admin = _is_admin(user)

    orig = db.query(AgentJob).filter(AgentJob.id == job_id, AgentJob.workspace_id == ws.id).first()
    if not orig:
        raise HTTPException(status_code=404, detail="Original job not found")
    if orig.status not in ("completed", "pending_financial_review"):
        raise HTTPException(status_code=400, detail="Can only revise completed jobs")

    meta = AGENT_CATALOGUE.get(orig.agent_id, {})
    credit_cost = meta.get("credit_estimate", 1)

    # Credit check and deduction — skipped entirely for admins (unlimited credits).
    if not is_admin:
        remaining = (cred.total_credits - cred.used_credits) if cred else 0
        if remaining < credit_cost:
            raise HTTPException(status_code=402, detail=f"Insufficient credits. Need {credit_cost}, have {remaining}.")
        if cred:
            cred = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == ws.id).with_for_update().first()
            if cred:
                cred.used_credits += credit_cost
                cred.updated_at = datetime.utcnow()

    now = datetime.utcnow()
    revision_input = json.loads(orig.input_data or "{}")
    if body.output_language:
        revision_input.setdefault("context", {})["output_language"] = body.output_language

    revision_job = AgentJob(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        agent_id=orig.agent_id,
        agent_name=orig.agent_name,
        status="pending",
        hitl_level=orig.hitl_level,
        input_data=json.dumps(revision_input),
        credits_used=credit_cost,
        revision_of=orig.id,
        revision_prompt=body.revision_prompt[:2000],
        output_language=body.output_language or orig.output_language,
        created_at=now,
        updated_at=now,
    )
    db.add(revision_job)
    db.commit()
    db.refresh(revision_job)

    return {
        "job_id": revision_job.id,
        "revision_of": orig.id,
        "agent_id": orig.agent_id,
        "status": "pending",
        "message": "Revision queued",
    }


# ---------------------------------------------------------------------------
# Scheduled runs
# ---------------------------------------------------------------------------

class ScheduleRunRequest(BaseModel):
    agent_id: str
    name: str = ""
    cron_expr: str          # "0 9 * * 1" = Mon 9am UTC
    prompt: str
    context: dict = {}


@router.get("/api/agents/schedules")
@limiter.limit("30/minute")
async def list_schedules(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    from app.models.agent_system import ScheduledRun
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        return {"schedules": []}
    rows = db.query(ScheduledRun).filter(ScheduledRun.workspace_id == ws.id).all()
    return {"schedules": [
        {"id": r.id, "agent_id": r.agent_id, "name": r.name, "cron_expr": r.cron_expr,
         "is_active": r.is_active, "last_run_at": r.last_run_at.isoformat() if r.last_run_at else None,
         "next_run_at": r.next_run_at.isoformat() if r.next_run_at else None}
        for r in rows
    ]}


@router.post("/api/agents/schedules")
@limiter.limit("10/minute")
async def create_schedule(
    request: Request,
    body: ScheduleRunRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    from app.models.agent_system import ScheduledRun
    from croniter import croniter  # type: ignore

    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found")

    norm_id = normalize_agent_id(body.agent_id)
    if norm_id not in AGENT_CATALOGUE:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {body.agent_id}")

    try:
        cron = croniter(body.cron_expr)
        next_run = cron.get_next(datetime)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid cron expression. Example: '0 9 * * 1' (Mon 9am UTC)")

    now = datetime.utcnow()
    sched = ScheduledRun(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        agent_id=norm_id,
        name=body.name or f"{AGENT_CATALOGUE[norm_id]['name']} — scheduled",
        cron_expr=body.cron_expr,
        prompt=body.prompt[:10_000],
        context=json.dumps(body.context) if body.context else None,
        is_active=True,
        next_run_at=next_run,
        created_at=now,
    )
    db.add(sched)
    db.commit()
    db.refresh(sched)

    return {"schedule_id": sched.id, "next_run_at": next_run.isoformat(), "message": "Schedule created"}


@router.delete("/api/agents/schedules/{schedule_id}")
@limiter.limit("10/minute")
async def delete_schedule(
    schedule_id: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    from app.models.agent_system import ScheduledRun
    user = _get_user(credentials, db)
    _, ws, _ = _workspace_tier(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")
    sched = db.query(ScheduledRun).filter(ScheduledRun.id == schedule_id, ScheduledRun.workspace_id == ws.id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(sched)
    db.commit()
    return {"deleted": schedule_id}


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
