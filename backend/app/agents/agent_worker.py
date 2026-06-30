"""
Agent Worker — async background loop that picks up and executes agent jobs.

Job lifecycle:
  pending           → picked up by worker → running → completed / failed
  pending_approval  → admin approves → approved → picked up by worker → running → ...
  approved          → picked up by worker → running → completed / failed

The worker runs inside the FastAPI lifespan (same process, asyncio background task).
For production scale this should move to a dedicated ECS worker service via SQS —
the same pattern used by the existing video worker. The interface is identical.
"""

import asyncio
import json
import logging
import os
from datetime import datetime

import sentry_sdk

import boto3

logger = logging.getLogger(__name__)

_CW_NAMESPACE = "Vantro/AgentJobs"
_AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
OWNER_ADMIN_BILLING_MODE = "owner_admin_unlimited"

_cloudwatch = None


def _get_cloudwatch():
    global _cloudwatch
    if _cloudwatch is None:
        try:
            _cloudwatch = boto3.client("cloudwatch", region_name=_AWS_REGION)
        except Exception:
            pass
    return _cloudwatch


def _emit_metric(metric_name: str, value: float, unit: str = "Count", dimensions: list | None = None) -> None:
    cw = _get_cloudwatch()
    if cw is None:
        return
    try:
        cw.put_metric_data(
            Namespace=_CW_NAMESPACE,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit,
                    "Dimensions": dimensions or [],
                }
            ],
        )
    except Exception as exc:
        logger.debug("CloudWatch emit failed: %s", exc)

def _positive_int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


POLL_INTERVAL_SECONDS       = _positive_int_env("AGENT_WORKER_POLL_INTERVAL_SECONDS", 5)
MAX_CONCURRENT_JOBS         = _positive_int_env("AGENT_WORKER_MAX_CONCURRENT_JOBS", 3)
STALE_JOB_MINUTES           = 15    # jobs stuck "running" longer than this are force-failed
STALE_CHECK_INTERVAL        = 60    # seconds between stale-job sweeps
REPORT_CHECK_INTERVAL       = 3600  # seconds between weekly report checks (1 hour)
SKILL_REINDEX_INTERVAL      = 21600 # seconds between skill freshness checks (6 hours)
BILLING_REMINDER_INTERVAL   = 86400 # seconds between billing reminder sweeps (24 hours)


def _claim_job_for_execution(db, job_id: str):
    """Atomically claim a runnable job so scaled workers cannot duplicate work."""
    from app.models.agent_system import AgentJob

    now = datetime.utcnow()
    updated = (
        db.query(AgentJob)
        .filter(AgentJob.id == job_id, AgentJob.status.in_(["pending", "approved"]))
        .update(
            {
                AgentJob.status: "running",
                AgentJob.updated_at: now,
            },
            synchronize_session=False,
        )
    )
    if updated != 1:
        db.rollback()
        return None

    db.commit()
    return db.query(AgentJob).filter(AgentJob.id == job_id).first()


def _selected_video_route(creative_provider_route: object) -> dict:
    if not isinstance(creative_provider_route, dict):
        return {}

    video_route = creative_provider_route.get("video")
    return video_route if isinstance(video_route, dict) else {}


def _should_execute_higgsfield_live(adapter_result, creative_provider_route: object) -> bool:
    if not getattr(adapter_result, "provider_ready", False):
        return False

    execution_payload = getattr(adapter_result, "execution_payload", None)
    if not isinstance(execution_payload, dict):
        return False

    video_route = _selected_video_route(creative_provider_route)
    selected_provider = execution_payload.get("selected_video_provider")
    selected_model = execution_payload.get("selected_video_model")
    route_provider = video_route.get("provider")
    route_model = video_route.get("model")

    return (
        selected_provider == "higgsfield"
        and route_provider == "higgsfield"
        and bool(selected_model)
        and selected_model == route_model
    )


def _first_media_url(value: object) -> str:
    if not isinstance(value, dict):
        return ""
    for key in ("asset_url", "media_url", "preview_url", "download_url", "video_url", "image_url"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return ""


def _job_context_from_input_data(input_data: object) -> dict:
    if not isinstance(input_data, str) or not input_data.strip():
        return {}
    try:
        parsed = json.loads(input_data)
    except (TypeError, ValueError):
        return {}
    if not isinstance(parsed, dict):
        return {}
    context = parsed.get("context")
    return context if isinstance(context, dict) else {}


def _job_uses_owner_admin_unlimited_billing(job: object) -> bool:
    context = _job_context_from_input_data(getattr(job, "input_data", ""))
    return (
        context.get("billing_mode") == OWNER_ADMIN_BILLING_MODE
        and context.get("credits_unlimited") is True
        and str(context.get("package_tier") or "").lower() == "enterprise"
    )


def _media_request_from_context(context: object) -> dict:
    if not isinstance(context, dict):
        return {}
    media_request = context.get("media_request")
    return media_request if isinstance(media_request, dict) else {}


def _clean_media_string(value: object, default: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _normalize_aspect_ratio(value: object) -> str:
    raw = _clean_media_string(value, "9:16")
    return raw.split(" ", 1)[0].strip() or "9:16"


def _build_elevenlabs_voiceover(language: str) -> dict:
    return {
        "provider": "elevenlabs",
        "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        "language": language,
        "multilingual": True,
    }


def _build_higgsfield_execution_kwargs(
    context: object,
    adapter_result: object,
    fallback_voiceover_script: str = "",
) -> dict:
    media_request = _media_request_from_context(context)
    execution_payload = getattr(adapter_result, "execution_payload", {})
    execution_payload = execution_payload if isinstance(execution_payload, dict) else {}
    route = execution_payload.get("creative_provider_route")
    video_route = _selected_video_route(route)
    language = _clean_media_string(
        media_request.get("language") or execution_payload.get("language"),
        "English",
    )
    quality = _clean_media_string(
        media_request.get("video_quality") or video_route.get("quality"),
        "1080p",
    )
    voiceover = _build_elevenlabs_voiceover(language)
    voiceover_script = _clean_media_string(
        media_request.get("voiceover_script")
        or media_request.get("voice_script")
        or media_request.get("narration_script")
        or media_request.get("voiceover")
        or fallback_voiceover_script,
        "",
    )

    return {
        "model": execution_payload.get("selected_video_model_id") or execution_payload.get("selected_video_model"),
        "duration": 30,
        "aspect_ratio": _normalize_aspect_ratio(media_request.get("aspect_ratio")),
        "platform": _clean_media_string(media_request.get("platform"), "tiktok").lower(),
        "tone": _clean_media_string(media_request.get("tone"), "professional").lower(),
        "quality": quality,
        "language": language,
        "voice_provider": voiceover["provider"],
        "voice_model_id": voiceover["model_id"],
        "voice_language": voiceover["language"],
        "voiceover_script": voiceover_script,
        "multilingual_voice_enabled": voiceover["multilingual"],
    }


def _resolve_billable_credit_cost(*, actual_credits: int, pre_committed: int, owner_admin_unlimited: bool) -> int:
    if owner_admin_unlimited:
        return 0
    return max(0, int(actual_credits or pre_committed or 0))


def _build_media_generation_output(
    *,
    script: str,
    creative_provider_route: object,
    adapter_result: object | None,
    live_task_result: object | None,
    requested_agent_id: str,
    fallback_preview_asset: object | None = None,
) -> dict:
    from app.integrations.execution_adapters import adapter_summary

    adapter_payload = adapter_summary(adapter_result) if adapter_result else {}
    execution_payload = adapter_payload.get("execution_payload") if isinstance(adapter_payload, dict) else {}
    execution_payload = execution_payload if isinstance(execution_payload, dict) else {}

    live_asset_url = _first_media_url(live_task_result)
    fallback_asset = fallback_preview_asset if isinstance(fallback_preview_asset, dict) else {}
    fallback_preview_url = _first_media_url(fallback_asset)
    preview_url = live_asset_url or fallback_preview_url
    download_url = live_asset_url or fallback_preview_url
    live_task = live_task_result if isinstance(live_task_result, dict) else None
    real_media_asset_created = bool(live_asset_url)

    return {
        "type": "media_generation",
        "requested_agent_id": requested_agent_id,
        "script": script,
        "creative_provider_route": creative_provider_route if isinstance(creative_provider_route, dict) else {},
        "provider_readiness": {
            "adapter_name": adapter_payload.get("adapter_name"),
            "execution_mode": adapter_payload.get("execution_mode"),
            "provider_ready": bool(adapter_payload.get("provider_ready")),
            "message": adapter_payload.get("message"),
            "next_steps": adapter_payload.get("next_steps") or [],
            "provider_connected": bool(execution_payload.get("provider_connected")),
            "live_execution_enabled": bool(execution_payload.get("live_execution_enabled")),
            "selected_video_provider": execution_payload.get("selected_video_provider"),
            "selected_video_model": execution_payload.get("selected_video_model"),
            "selected_video_model_id": execution_payload.get("selected_video_model_id"),
            "selected_image_provider": execution_payload.get("selected_image_provider"),
            "selected_image_model": execution_payload.get("selected_image_model"),
            "language": execution_payload.get("language"),
            "voiceover": execution_payload.get("voiceover") or {},
        },
        "provider_task": live_task,
        "fallback_preview_asset": fallback_asset,
        "real_media_asset_created": real_media_asset_created,
        "preview_ready": bool(preview_url),
        "preview_url": preview_url,
        "download_ready": bool(download_url),
        "download_url": download_url,
        "asset_url": live_asset_url,
        "credential_values_exposed": False,
    }


async def _process_job(job_id: str) -> None:
    """Process a single agent job end-to-end."""

    # Local imports to avoid circular imports at module load
    from app.database import SessionLocal
    from app.models.agent_system import AgentJob
    from app.models.workspace import CreditsAccount, Workspace
    from app.agents.agent_prompts import get_agent_system_prompt
    from app.agents.agent_executor import execute_agent
    from app.agents.agent_registry import get_agent_credit_estimate, agent_exists, get_agent_hitl

    _sentry_txn = None
    db = SessionLocal()
    try:
        job = _claim_job_for_execution(db, job_id)
        if not job:
            logger.debug("Worker: job %s was already claimed or is not runnable, skipping", job_id)
            return

        logger.info("Worker: executing agent=%s job=%s", job.agent_id, job_id)
        _job_start_time = datetime.utcnow()
        _sentry_txn = sentry_sdk.start_transaction(op="agent.job", name=f"agent:{job.agent_id}")
        _sentry_txn.set_tag("agent_id", job.agent_id)
        _sentry_txn.set_data("workspace_id", str(job.workspace_id))
        _sentry_txn.set_data("job_id", job_id)
        sentry_sdk.set_user({"id": str(job.workspace_id)})
        sentry_sdk.logger.info("Agent job {job_id} started for agent {agent_id}", agent_id=str(job.agent_id), job_id=job_id)

        system_prompt = get_agent_system_prompt(job.agent_id)
        user_prompt   = job.input_data or ""

        # Parse optional context JSON stored in input_data
        context = {}
        try:
            parsed = json.loads(user_prompt)
            if isinstance(parsed, dict) and "prompt" in parsed:
                user_prompt = parsed["prompt"]
                context = parsed.get("context", {})
        except (json.JSONDecodeError, TypeError):
            pass

        # Inject workspace business_context + brand profile into context dict
        try:
            ws = db.query(Workspace).filter(Workspace.id == job.workspace_id).first()
            if ws and getattr(ws, "business_context", None):
                context["_workspace_context"] = ws.business_context
            # Brand profile: resolve workspace → org → user.brand_profile
            if ws:
                from app.models import Organization, User as _User
                org = db.query(Organization).filter(Organization.id == ws.organization_id).first()
                if org:
                    owner = db.query(_User).filter(_User.id == org.owner_id).first()
                    if owner and getattr(owner, "brand_profile", None):
                        import json as _json
                        bp = owner.brand_profile
                        context["_brand_profile"] = _json.dumps(bp) if isinstance(bp, dict) else str(bp)
        except Exception:
            pass

        # Parse output_language from job input context (if client specified one)
        _output_language: str | None = None
        try:
            _parsed_input = json.loads(job.input_data or "{}")
            _output_language = _parsed_input.get("context", {}).get("output_language")
            if _output_language:
                job.output_language = _output_language
        except Exception:
            pass

        # RAG: retrieve relevant skill chunks for this task (non-blocking — silent on failure)
        try:
            from app.services.skill_retriever import retrieve_relevant_skills
            _skill_ctx = retrieve_relevant_skills(db, user_prompt)
            if _skill_ctx:
                context["_skill_context"] = _skill_ctx
        except Exception:
            pass

        # Few-shot: inject quality-reference examples for this agent (non-blocking)
        try:
            from app.services.example_retriever import get_few_shot_examples
            _examples = get_few_shot_examples(db, job.agent_id)
            if _examples:
                context["_few_shot_examples"] = _examples
        except Exception:
            pass

        # Composio: pass workspace credentials so executor can build live tool list (non-blocking)
        try:
            from app.services.composio_service import get_composio_credentials
            _creds = get_composio_credentials(db, job.workspace_id)
            if _creds:
                context["_composio_api_key"], context["_composio_entity_id"] = _creds
        except Exception:
            pass

        # Workspace memory: inject top-3 recent outcomes for this agent (non-blocking)
        try:
            from sqlalchemy import text as _text
            _mem_rows = db.execute(
                _text(
                    "SELECT encrypted_value FROM workspace_integrations"
                    " WHERE workspace_id=:ws AND integration_name='agent_memory'"
                    "   AND integration_key LIKE :prefix"
                    " ORDER BY created_at DESC LIMIT 3"
                ),
                {"ws": job.workspace_id, "prefix": f"AGENT_MEMORY_{job.agent_id}%"},
            ).fetchall()
            if _mem_rows:
                context["_workspace_memory"] = "\n".join(r[0] for r in _mem_rows)
        except Exception:
            pass

        hitl_level = get_agent_hitl(job.agent_id)
        _sentry_txn.set_tag("hitl_level", hitl_level)

        # Mark step: execution started
        _step_ts = datetime.utcnow().isoformat()
        job.steps = json.dumps([
            {"step": "Queued",          "status": "done", "ts": job.created_at.isoformat() if job.created_at else _step_ts},
            {"step": "Executing agent", "status": "running", "ts": _step_ts},
        ])
        db.commit()

        # Fetch revision context if this job is a revision
        _revision_output: str | None = None
        _revision_prompt_text: str | None = None
        try:
            if getattr(job, "revision_of", None):
                orig = db.query(AgentJob).filter(AgentJob.id == job.revision_of).first()
                if orig and orig.output_data:
                    _revision_output = orig.output_data.split(" -->\n", 1)[-1]
                _revision_prompt_text = getattr(job, "revision_prompt", None)
        except Exception:
            pass

        with _sentry_txn.start_child(op="llm.execute", description=f"agent:{job.agent_id}") as _llm_span:
            _llm_span.set_data("hitl_level", hitl_level)
            output, provider_used, actual_credits, financial_violations, prompt_version = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: execute_agent(
                    agent_id=job.agent_id,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    context=context,
                    workspace_id=job.workspace_id,
                    hitl_level=hitl_level,
                    output_language=_output_language,
                    revision_of_output=_revision_output,
                    revision_prompt=_revision_prompt_text,
                ),
            )

        job.agent_version   = prompt_version
        job.prompt_snapshot = system_prompt[:4000]  # cap to avoid DB bloat

        owner_admin_unlimited = _job_uses_owner_admin_unlimited_billing(job)

        # actual_credits is derived from real token usage; adjust the pre-committed
        # estimate up or down accordingly. Owner/admin Enterprise jobs are
        # metered for provider diagnostics only and never mutate client credits.
        pre_committed = job.credits_used or 0
        credit_cost = _resolve_billable_credit_cost(
            actual_credits=actual_credits,
            pre_committed=pre_committed,
            owner_admin_unlimited=owner_admin_unlimited,
        )
        cred = (
            db.query(CreditsAccount)
            .join(Workspace, Workspace.id == CreditsAccount.workspace_id)
            .filter(Workspace.id == job.workspace_id)
            .with_for_update()
            .first()
        )
        delta = credit_cost - pre_committed  # positive = underpaid, negative = refund
        if cred and delta != 0 and not owner_admin_unlimited:
            cred.used_credits = max(0, min(cred.total_credits, cred.used_credits + delta))
            cred.updated_at = datetime.utcnow()

        now = datetime.utcnow()

        # ── Financial governance gate ────────────────────────────────────────
        # If the output scanner detected financial-action language (the agent
        # attempted to authorise/commit a financial action instead of suggesting),
        # hold the job in pending_financial_review so a human can inspect and
        # decide whether to release or reject the output.
        # This fires regardless of HITL level — it is a hard platform rule.
        if financial_violations:
            sentry_sdk.logger.warning("Agent job {job_id} held for financial review ({violation_count} violations)", agent_id=str(job.agent_id), job_id=job_id, violation_count=len(financial_violations))
            logger.warning(
                "Worker: job %s held for financial review — violations: %s",
                job_id, financial_violations,
            )
            job.status      = "pending_financial_review"
            job.output_data = output
            job.credits_used = credit_cost
            job.updated_at  = now
            # Notify admin
            try:
                admin_email = os.getenv("ADMIN_EMAIL", "")
                if admin_email:
                    from app.services.email_service import _send as _send_email
                    _send_email(
                        admin_email,
                        f"[ACTION REQUIRED] Agent output held for financial review — job {job_id}",
                        (
                            f"Job {job_id} (agent: {job.agent_id}) produced output that matched "
                            f"financial-action language and has been held for your review.\n\n"
                            f"Matched phrases: {', '.join(financial_violations)}\n\n"
                            f"Review and release or reject this job in the Admin > Approvals panel."
                        ),
                        None,
                    )
            except Exception:
                pass
            db.commit()
            _sentry_txn.set_tag("outcome", "financial_review")
            _sentry_txn.finish()
            return
        # ────────────────────────────────────────────────────────────────────

        # Confidence auto-escalation: if agent output signals low confidence,
        # hold the job for human review before marking it completed.
        import re as _re
        _confidence_low = bool(_re.search(r'\[CONFIDENCE:\s*LOW\]', output, _re.IGNORECASE))
        if _confidence_low and job.status not in ("pending_financial_review",):
            sentry_sdk.logger.warning("Agent job {job_id} escalated to pending_approval (CONFIDENCE: LOW)", agent_id=str(job.agent_id), job_id=job_id)
            logger.warning(
                "Worker: job %s escalated to pending_approval — agent output [CONFIDENCE: LOW]",
                job_id,
            )
            job.status = "pending_approval"
            job.output_data = output
            job.credits_used = credit_cost
            job.updated_at = now
            db.commit()
            # Notify workspace owner that their job is held for approval
            try:
                from app.services.email_service import send_approval_needed_owner
                from app.models import Organization
                from app.models import User as _NotifyUser
                ws_obj = db.query(Workspace).filter(Workspace.id == job.workspace_id).first()
                if ws_obj:
                    org_obj = db.query(Organization).filter(Organization.id == ws_obj.organization_id).first()
                    if org_obj:
                        owner_obj = db.query(_NotifyUser).filter(_NotifyUser.id == org_obj.owner_id).first()
                        if owner_obj:
                            send_approval_needed_owner(
                                owner_email=owner_obj.email,
                                owner_name=getattr(owner_obj, "name", None) or owner_obj.email,
                                agent_name=getattr(job, "agent_name", None) or job.agent_id,
                                job_id=job_id,
                            )
            except Exception:
                pass
            _sentry_txn.set_tag("outcome", "confidence_escalated")
            _sentry_txn.finish()
            return

        # ── Media provider routing for ugc_media_agent ──────────────────────────
        # For UGC media jobs, route the LLM-generated brief to Higgsfield for
        # actual video generation. The output from execute_agent is the creative
        # brief/script; Higgsfield will generate the video asset.
        media_provider_output = output
        try:
            from app.runtime.creative_provider_routing import is_creative_agent, resolve_creative_provider_route
            from app.integrations.execution_adapters import ExecutionAdapters
            if is_creative_agent(job.agent_id):
                adapters = ExecutionAdapters(db=db)
                creative_provider_route = context.get("creative_provider_route")
                media_request = _media_request_from_context(context)
                media_language = _clean_media_string(media_request.get("language"), "English")
                media_voiceover = _build_elevenlabs_voiceover(media_language)
                requested_agent_id = str(
                    context.get("requested_creative_agent_id")
                    or context.get("selected_creative_agent_id")
                    or job.agent_id
                )
                if not isinstance(creative_provider_route, dict) or not creative_provider_route.get("success"):
                    creative_provider_route = resolve_creative_provider_route(
                        agent_id=requested_agent_id,
                        media_type="both",
                        request_context=context,
                    )

                live_task_result = None
                adapter_result = adapters.execute(
                    adapter_name="ugc_video_provider_adapter",
                    payload={
                        "workflow": {
                            "tenant_id": job.workspace_id,
                            "task": output[:1000],
                            "region": "Global",
                            "language": media_language,
                            "media_request": media_request,
                            "voiceover": media_voiceover,
                            "creative_provider_route": creative_provider_route,
                        },
                        "context": {
                            "agent_id": job.agent_id,
                            "job_id": job.id,
                            "media_request": media_request,
                            "creative_provider_route": creative_provider_route,
                        },
                    },
                )

                if _should_execute_higgsfield_live(adapter_result, creative_provider_route):
                    higgsfield = adapter_result.execution_payload.get("provider_instance")
                    if higgsfield:
                        try:
                            higgsfield_kwargs = _build_higgsfield_execution_kwargs(
                                context,
                                adapter_result,
                                fallback_voiceover_script=output,
                            )
                            live_task_result = await higgsfield.execute(
                                prompt=output,
                                **higgsfield_kwargs,
                            )
                            logger.info("Worker: UGC media job %s routed to Higgsfield", job_id)
                        except Exception as e:
                            logger.error("Worker: Higgsfield execution failed for job %s: %s", job_id, e)
                            live_task_result = {"error": str(e), "provider": "higgsfield"}

                fallback_preview_asset = None
                if not _first_media_url(live_task_result):
                    try:
                        from app.runtime.shared_creative_visual_generation_runtime import generate_creative_visual_asset
                        fallback_preview_asset = generate_creative_visual_asset(
                            prompt=output,
                            agent_id=requested_agent_id,
                            tenant_id=job.workspace_id,
                            asset_kind="creative_media_preview_asset",
                        )
                    except Exception as preview_exc:
                        logger.warning(
                            "Worker: fallback preview generation failed for job %s: %s",
                            job_id,
                            preview_exc,
                        )

                media_provider_output = json.dumps(
                    _build_media_generation_output(
                        script=output,
                        creative_provider_route=creative_provider_route,
                        adapter_result=adapter_result,
                        live_task_result=live_task_result,
                        requested_agent_id=requested_agent_id,
                        fallback_preview_asset=fallback_preview_asset,
                    ),
                    sort_keys=True,
                )
        except Exception as e:
            logger.error("Worker: Media adapter setup failed for job %s: %s", job_id, e)
        # ────────────────────────────────────────────────────────────────────────

        job.status       = "completed"
        job.output_data  = f"<!-- provider:{provider_used} -->\n{media_provider_output}"
        job.credits_used = credit_cost
        job.updated_at   = now
        job.completed_at = now
        job.steps = json.dumps([
            {"step": "Queued",          "status": "done", "ts": job.created_at.isoformat() if job.created_at else now.isoformat()},
            {"step": "Executing agent", "status": "done", "ts": _step_ts},
            {"step": "Completed",       "status": "done", "ts": now.isoformat()},
        ])
        db.commit()

        logger.info(
            "Worker: job %s completed via %s (%d credits deducted)",
            job_id, provider_used, credit_cost,
        )
        _sentry_txn.set_measurement("credits_used", credit_cost)
        _sentry_txn.set_tag("outcome", "completed")
        _sentry_txn.set_tag("provider", provider_used.split("/")[0] if provider_used else "unknown")
        _sentry_txn.finish()
        sentry_sdk.logger.info(
            "Agent job {job_id} completed",
            attributes={
                "job.id": job_id,
                "agent.id": str(job.agent_id),
                "agent.hitl_level": hitl_level,
                "job.credits_used": credit_cost,
                "job.provider": provider_used.split("/")[0] if provider_used else "unknown",
                "job.provider_model": provider_used or "unknown",
                "job.duration_ms": round((datetime.utcnow() - _job_start_time).total_seconds() * 1000),
                "workspace.id": str(job.workspace_id),
            },
        )
        ws_dims = [{"Name": "WorkspaceId", "Value": str(job.workspace_id)}]
        _emit_metric("AgentJobsCompleted", 1, dimensions=ws_dims)
        _emit_metric("CreditsDeducted", credit_cost, dimensions=ws_dims)

        # Persist outcome to workspace memory (async, best-effort)
        asyncio.create_task(
            _save_workspace_outcome_memory(job_id, job.workspace_id, job.agent_id, output)
        )

    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        sentry_sdk.logger.error(
            "Agent job {job_id} failed",
            attributes={
                "job.id": job_id,
                "error.message": str(exc)[:500],
                "error.type": type(exc).__name__,
            },
        )
        if _sentry_txn is not None:
            _sentry_txn.set_tag("outcome", "failed")
            _sentry_txn.finish()
        logger.error("Worker: job %s failed: %s", job_id, exc, exc_info=True)
        try:
            job = db.query(AgentJob).filter(AgentJob.id == job_id).first()
            if job:
                ws_dims = [{"Name": "WorkspaceId", "Value": str(job.workspace_id)}]
                _emit_metric("AgentJobsFailed", 1, dimensions=ws_dims)
                # Refund pre-committed credits on failure
                pre_committed = job.credits_used or 0
                if pre_committed > 0:
                    cred = (
                        db.query(CreditsAccount)
                        .join(Workspace, Workspace.id == CreditsAccount.workspace_id)
                        .filter(Workspace.id == job.workspace_id)
                        .first()
                    )
                    if cred:
                        cred.used_credits = max(0, cred.used_credits - pre_committed)
                        cred.updated_at = datetime.utcnow()
                job.status        = "failed"
                job.error_message = str(exc)[:2000]
                job.credits_used  = 0  # refunded
                job.updated_at    = datetime.utcnow()
                db.commit()
        except Exception as db_exc:
            logger.error("Worker: failed to update job status: %s", db_exc)
    finally:
        db.close()


async def _recover_stale_jobs() -> None:
    """Reset jobs stuck in 'running' for longer than STALE_JOB_MINUTES to 'failed'."""
    from app.database import SessionLocal
    from app.models.agent_system import AgentJob
    from app.models.workspace import CreditsAccount, Workspace

    stale_cutoff = datetime.utcnow() - __import__("datetime").timedelta(minutes=STALE_JOB_MINUTES)
    db = SessionLocal()
    try:
        stale = (
            db.query(AgentJob)
            .filter(AgentJob.status == "running", AgentJob.updated_at < stale_cutoff)
            .all()
        )
        for job in stale:
            logger.warning("Worker: force-failing stale job %s (stuck running since %s)", job.id, job.updated_at)
            # Refund any pre-committed credits
            pre_committed = job.credits_used or 0
            if pre_committed > 0:
                cred = (
                    db.query(CreditsAccount)
                    .join(Workspace, Workspace.id == CreditsAccount.workspace_id)
                    .filter(Workspace.id == job.workspace_id)
                    .first()
                )
                if cred:
                    cred.used_credits = max(0, cred.used_credits - pre_committed)
                    cred.updated_at = datetime.utcnow()
            job.status = "failed"
            job.error_message = f"Job timed out after {STALE_JOB_MINUTES} minutes"
            job.credits_used = 0
            job.updated_at = datetime.utcnow()
        if stale:
            db.commit()
            logger.info("Worker: recovered %d stale job(s)", len(stale))
    except Exception as exc:
        logger.error("Worker: stale job recovery error: %s", exc)
    finally:
        db.close()


async def _run_weekly_reports() -> None:
    """
    Generate and email weekly reports for workspaces that have reached their
    configured send day/hour (UTC). Called hourly from the main worker loop.
    Skips workspaces that already received a report within the past 6 days.
    """
    from datetime import timedelta
    from app.database import SessionLocal
    from app.models.workspace import Workspace
    from app.models.reports import WorkspaceReportSettings, WeeklyReport
    from app.services.weekly_report_service import generate_workspace_report, send_report_email

    now = datetime.utcnow()
    weekday_name = now.strftime("%A").lower()

    db = SessionLocal()
    try:
        due_settings = (
            db.query(WorkspaceReportSettings)
            .filter(
                WorkspaceReportSettings.enabled == True,
                WorkspaceReportSettings.schedule_day == weekday_name,
                WorkspaceReportSettings.schedule_hour == now.hour,
            )
            .all()
        )
        for settings in due_settings:
            try:
                recent = (
                    db.query(WeeklyReport)
                    .filter(
                        WeeklyReport.workspace_id == settings.workspace_id,
                        WeeklyReport.created_at >= now - timedelta(days=6),
                    )
                    .first()
                )
                if recent:
                    continue

                report = generate_workspace_report(settings.workspace_id, db)
                recipients = list(settings.recipients or [])

                if not recipients:
                    ws = db.query(Workspace).filter(Workspace.id == settings.workspace_id).first()
                    if ws:
                        from app.models import Organization, User
                        org = db.query(Organization).filter(Organization.id == ws.organization_id).first()
                        if org:
                            owner = db.query(User).filter(User.id == org.owner_id).first()
                            if owner and owner.email:
                                recipients = [owner.email]

                if recipients:
                    send_report_email(report, recipients, db)

            except Exception as exc:
                logger.error("Weekly report failed for workspace %s: %s", settings.workspace_id, exc)
    except Exception as exc:
        logger.error("Weekly report scheduler error: %s", exc)
    finally:
        db.close()


async def _reindex_new_skills() -> None:
    """
    Auto-index any skills installed in ~/.claude/skills/ since the last run.
    Detects: (a) brand-new skill dirs, (b) SKILL.md files modified after last index.
    Silent on failure — skill RAG is best-effort, never blocks job execution.
    Requires OPENAI_API_KEY to embed; skips silently if not configured.
    """
    if not os.getenv("OPENAI_API_KEY", "").strip():
        return
    from app.database import SessionLocal
    from app.services.skill_indexer import get_skills_needing_index, index_skills_by_name

    db = SessionLocal()
    try:
        needing = get_skills_needing_index(db)
        if not needing:
            return
        logger.info("Worker: auto-indexing %d new/updated skill(s): %s", len(needing), needing)
        result = index_skills_by_name(db, needing)
        if result["indexed"]:
            logger.info(
                "Worker: skill auto-index complete — %d skill(s), %d chunks",
                result["indexed"], result["total_chunks"],
            )
        if result["failed"]:
            logger.warning("Worker: skill auto-index failures: %s", result["failed"])
    except Exception as exc:
        logger.debug("Worker: skill auto-index error: %s", exc)
    finally:
        db.close()


async def _save_workspace_outcome_memory(job_id: str, workspace_id: str, agent_id: str, output_text: str) -> None:
    """
    Persist a compressed summary of a completed job to workspace memory.
    On future runs for same workspace, top-3 memories injected as context.
    Best-effort — never blocks job completion.
    """
    from app.database import SessionLocal
    from sqlalchemy import text
    try:
        summary = f"[{agent_id}] {output_text[:500]}".replace("\n", " ")
        db = SessionLocal()
        try:
            # Store in a simple key-value memory table (uses existing workspace_integrations pattern)
            # Uses a special integration_key namespace "AGENT_MEMORY_*"
            mem_key = f"AGENT_MEMORY_{agent_id}_{job_id[:8]}"
            db.execute(
                text(
                    "INSERT INTO workspace_integrations "
                    "(id, workspace_id, integration_key, integration_name, encrypted_value, is_active, created_at)"
                    " VALUES (:id, :ws, :key, :name, :val, true, :ts)"
                    " ON CONFLICT DO NOTHING"
                ),
                {
                    "id": str(__import__("uuid").uuid4()),
                    "ws": workspace_id,
                    "key": mem_key,
                    "name": "agent_memory",
                    "val": summary[:1000],
                    "ts": datetime.utcnow(),
                },
            )
            db.commit()
        finally:
            db.close()
    except Exception as exc:
        logger.debug("Workspace memory save error for job %s: %s", job_id, exc)


async def _run_scheduled_agents() -> None:
    """
    Every 5 minutes: check for ScheduledRun rows whose next_run_at has passed,
    create an AgentJob for each, and advance next_run_at.
    """
    from datetime import datetime
    from sqlalchemy import text
    from app.database import SessionLocal
    import uuid as _uuid
    try:
        from croniter import croniter as _croniter  # type: ignore
    except ImportError:
        logger.debug("croniter not installed — scheduled runs skipped")
        return

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        from app.models.agent_system import ScheduledRun, AgentJob as _AgentJob
        due = db.query(ScheduledRun).filter(
            ScheduledRun.is_active == True,
            ScheduledRun.next_run_at <= now,
        ).all()
        for sched in due:
            try:
                from app.agents.agent_registry import AGENT_CATALOGUE, get_agent_hitl
                meta = AGENT_CATALOGUE.get(sched.agent_id, {})
                credit_cost = meta.get("credit_estimate", 1)
                hitl = get_agent_hitl(sched.agent_id)
                ctx = {}
                if sched.context:
                    try:
                        ctx = json.loads(sched.context)
                    except Exception:
                        pass
                job = _AgentJob(
                    id=str(_uuid.uuid4()),
                    workspace_id=sched.workspace_id,
                    agent_id=sched.agent_id,
                    agent_name=meta.get("name", sched.agent_id),
                    status="pending" if hitl != "HITL-3" else "pending_approval",
                    hitl_level=hitl,
                    input_data=json.dumps({"prompt": sched.prompt, "context": ctx, "_scheduled_run_id": sched.id}),
                    credits_used=credit_cost,
                    created_at=now,
                    updated_at=now,
                )
                db.add(job)
                sched.last_run_at = now
                cron = _croniter(sched.cron_expr, now)
                sched.next_run_at = cron.get_next(datetime)
                logger.info("Scheduled run triggered: agent=%s schedule=%s", sched.agent_id, sched.id)
            except Exception as exc:
                logger.error("Scheduled run error for schedule %s: %s", sched.id, exc)
        db.commit()
    except Exception as exc:
        logger.error("Scheduled run sweep error: %s", exc)
    finally:
        db.close()


async def _send_billing_reminder_emails() -> None:
    """
    Daily sweep: find users whose subscription renews in ~2 days and send a heads-up email.
    Billing itself is handled by Stripe (billing_cycle_anchor set 28 days out at subscription
    creation so Stripe charges 2 days before the natural monthly anniversary).
    """
    from datetime import datetime, timedelta
    from sqlalchemy import text
    from app.database import SessionLocal
    from app.services.email_service import send_billing_reminder

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        window_start = now + timedelta(hours=47)
        window_end = now + timedelta(hours=49)
        rows = db.execute(
            text(
                "SELECT id, email, name, subscription_period_end FROM users"
                " WHERE subscription_status='active'"
                "   AND subscription_period_end IS NOT NULL"
                "   AND subscription_period_end BETWEEN :s AND :e"
            ),
            {"s": window_start, "e": window_end},
        ).fetchall()
        for row in rows:
            try:
                send_billing_reminder(
                    to_email=row.email,
                    name=row.name or "there",
                    renewal_date=row.subscription_period_end,
                )
                logger.info("Billing reminder sent to user %s", row.id)
            except Exception as exc:
                logger.error("Billing reminder email failed for user %s: %s", row.id, exc)
    except Exception as exc:
        logger.error("Billing reminder sweep error: %s", exc)
    finally:
        db.close()


DATA_RETENTION_INTERVAL = 86400  # 24 hours


async def _enforce_data_retention() -> None:
    """
    Daily sweep to purge old rows per retention policy:
    - agent_jobs completed > 90 days ago
    - audit_logs > 365 days old
    - webhooks_log > 30 days old (table may not exist — silently skipped)
    """
    from datetime import datetime, timedelta
    from sqlalchemy import text
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        cutoff_jobs = now - timedelta(days=90)
        cutoff_audit = now - timedelta(days=365)
        cutoff_webhooks = now - timedelta(days=30)

        result = db.execute(
            text(
                "DELETE FROM agent_jobs"
                " WHERE status = 'completed'"
                "   AND created_at < :cutoff"
            ),
            {"cutoff": cutoff_jobs},
        )
        jobs_deleted = result.rowcount
        logger.info("Data retention: deleted %d completed agent_jobs older than 90 days", jobs_deleted)

        result = db.execute(
            text("DELETE FROM audit_logs WHERE created_at < :cutoff"),
            {"cutoff": cutoff_audit},
        )
        audit_deleted = result.rowcount
        logger.info("Data retention: deleted %d audit_logs older than 365 days", audit_deleted)

        try:
            result = db.execute(
                text("DELETE FROM webhooks_log WHERE created_at < :cutoff"),
                {"cutoff": cutoff_webhooks},
            )
            hooks_deleted = result.rowcount
            logger.info("Data retention: deleted %d webhooks_log rows older than 30 days", hooks_deleted)
        except Exception as exc:
            logger.debug("Data retention: webhooks_log sweep skipped (%s)", exc)

        db.commit()
    except Exception as exc:
        logger.error("Data retention sweep error: %s", exc)
    finally:
        db.close()


async def run_agent_worker() -> None:
    """
    Main worker loop. Polls the DB every POLL_INTERVAL_SECONDS for
    jobs in 'pending' or 'approved' state and processes them concurrently.
    """
    logger.info("Agent worker started (poll interval: %ds)", POLL_INTERVAL_SECONDS)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)
    _stale_check_counter = 0
    _report_check_counter = 0
    _skill_check_counter          = SKILL_REINDEX_INTERVAL  # fire immediately on first tick
    _billing_reminder_counter     = 0
    _schedule_check_counter       = 0
    _data_retention_counter       = 0

    # Run data retention once at startup (non-blocking)
    asyncio.create_task(_enforce_data_retention())

    async def _guarded_process(job_id: str) -> None:
        async with semaphore:
            await _process_job(job_id)

    while True:
        try:
            from app.database import SessionLocal
            from app.models.agent_system import AgentJob

            # Periodic stale-job recovery sweep
            _stale_check_counter += POLL_INTERVAL_SECONDS
            if _stale_check_counter >= STALE_CHECK_INTERVAL:
                _stale_check_counter = 0
                asyncio.create_task(_recover_stale_jobs())

            # Hourly weekly report scheduler
            _report_check_counter += POLL_INTERVAL_SECONDS
            if _report_check_counter >= REPORT_CHECK_INTERVAL:
                _report_check_counter = 0
                asyncio.create_task(_run_weekly_reports())

            # Skill freshness check: auto-index new/updated skills every 6h
            _skill_check_counter += POLL_INTERVAL_SECONDS
            if _skill_check_counter >= SKILL_REINDEX_INTERVAL:
                _skill_check_counter = 0
                asyncio.create_task(_reindex_new_skills())

            # Billing reminder: send renewal notices to users 2 days before charge (daily)
            _billing_reminder_counter += POLL_INTERVAL_SECONDS
            if _billing_reminder_counter >= BILLING_REMINDER_INTERVAL:
                _billing_reminder_counter = 0
                asyncio.create_task(_send_billing_reminder_emails())

            # Data retention: purge old rows daily
            _data_retention_counter += POLL_INTERVAL_SECONDS
            if _data_retention_counter >= DATA_RETENTION_INTERVAL:
                _data_retention_counter = 0
                asyncio.create_task(_enforce_data_retention())

            # Scheduled agent runs: check every 5 minutes
            _schedule_check_counter += POLL_INTERVAL_SECONDS
            if _schedule_check_counter >= 300:
                _schedule_check_counter = 0
                asyncio.create_task(_run_scheduled_agents())

            db = SessionLocal()
            try:
                runnable = (
                    db.query(AgentJob.id)
                    .filter(AgentJob.status.in_(["pending", "approved"]))
                    .limit(MAX_CONCURRENT_JOBS * 2)
                    .all()
                )
                job_ids = [row.id for row in runnable]
            finally:
                db.close()

            if job_ids:
                logger.debug("Worker: found %d runnable job(s)", len(job_ids))
                tasks = [asyncio.create_task(_guarded_process(jid)) for jid in job_ids]
                await asyncio.gather(*tasks, return_exceptions=True)

        except asyncio.CancelledError:
            logger.info("Agent worker shutting down")
            break
        except Exception as exc:
            logger.error("Worker poll error: %s", exc, exc_info=True)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)
