from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

backup_dir = ROOT / "backups" / f"main_before_creative_media_execution_path_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "main.py").write_text(text, encoding="utf-8")

import_line = (
    "from backend.app.runtime.shared_creative_media_generation_runtime import "
    "generate_creative_media_pack, CREATIVE_MEDIA_AGENTS"
)

if import_line not in text:
    marker = "from backend.app.runtime.asset_storage_signed_delivery_runtime import build_customer_safe_delivery_response"
    if marker not in text:
        raise SystemExit("Import marker not found. No changes made.")
    text = text.replace(marker, marker + "\n" + import_line)

block_marker = "    workflow_engine = EcommerceWorkflowEngine()"

creative_media_block = '''    # CREATIVE_TEAM_REAL_MEDIA_EXECUTION_PATH_START
    creative_media_keywords = {
        "actual video",
        "generate video",
        "create video",
        "video ad",
        "ugc video",
        "short-form video",
        "reels",
        "tiktok",
        "voiceover",
        "audio",
        "avatar",
        "lip sync",
        "lipsync",
        "image asset",
        "product image",
        "creative asset",
        "media asset",
        "runway",
        "kling",
        "heygen",
        "elevenlabs",
        "visual",
        "ad creative",
        "campaign creative",
        "media execution pack",
        "preview/download-ready",
        "preview ready",
        "download ready",
    }

    creative_request_text = " ".join(
        [
            str(request.task or ""),
            str(request.action_type or ""),
            str(request.workflow_stage or ""),
            str(requested_agent or ""),
        ]
    ).lower().replace("_", " ")

    creative_media_requested = (
        requested_agent in CREATIVE_MEDIA_AGENTS
        or any(keyword in creative_request_text for keyword in creative_media_keywords)
    )

    if creative_media_requested:
        owner_media_execution_allowed = bool(
            owner_admin_internal_execution
            or request.owner_approved
            or actor_role in {"owner", "admin", "owner_admin", "system"}
        )

        if not owner_media_execution_allowed:
            return {
                "success": False,
                "status": "blocked_owner_approval_required",
                "workflow_status": "creative_media_execution_blocked",
                "execution_status": "blocked_owner_approval_required",
                "requested_agent": requested_agent,
                "tenant_id": request.tenant_id,
                "owner_approval_required": True,
                "external_provider_called": False,
                "spend_performed": False,
                "credential_values_exposed": False,
                "customer_safe": True,
                "message": "Creative media generation can call live media providers and requires owner approval.",
            }

        try:
            media_pack = generate_creative_media_pack(
                task=request.task,
                agent_id=requested_agent,
                tenant_id=request.tenant_id or "owner_admin",
                include_image=True,
                include_audio=True,
                include_video=True,
                include_avatar=True,
            )

            media_assets = media_pack.get("media_assets", []) if isinstance(media_pack, dict) else []
            provider_results = media_pack.get("provider_execution_results", []) if isinstance(media_pack, dict) else []
            generation_jobs = media_pack.get("generation_jobs", []) if isinstance(media_pack, dict) else []

            real_media_asset_count = int(media_pack.get("real_media_asset_count", 0) or 0) if isinstance(media_pack, dict) else 0
            provider_attempted_count = int(media_pack.get("live_provider_execution_attempted_count", 0) or 0) if isinstance(media_pack, dict) else 0

            execution_status = (
                "creative_live_media_generated"
                if real_media_asset_count > 0
                else "creative_media_provider_execution_attempted"
                if provider_attempted_count > 0
                else "creative_media_provider_not_available"
            )

            creative_payload = {
                "workflow_status": "creative_media_execution_completed",
                "execution_status": execution_status,
                "requested_agent": requested_agent,
                "tenant_id": request.tenant_id,
                "project_id": request.project_id,
                "media_pack": media_pack,
                "media_asset_count": len(media_assets),
                "real_media_asset_count": real_media_asset_count,
                "provider_attempted_count": provider_attempted_count,
                "generation_job_count": len(generation_jobs),
                "credential_values_exposed": False,
                "customer_safe": True,
            }

            try:
                MemoryStore().add_record(
                    tenant_id=request.tenant_id,
                    project_id=request.project_id,
                    record_type="creative_media_execution",
                    title=f"{requested_agent} creative media execution",
                    payload=creative_payload,
                )
            except Exception:
                pass

            try:
                SQLiteStore().add_record(
                    tenant_id=request.tenant_id,
                    project_id=request.project_id,
                    record_type="creative_media_execution",
                    title=f"{requested_agent} creative media execution",
                    payload=creative_payload,
                )
            except Exception:
                pass

            try:
                add_execution_event(
                    tenant_id=request.tenant_id,
                    project_id=request.project_id,
                    event_type="creative_media_execution_completed",
                    title=f"{requested_agent} creative media execution completed",
                    agent_id=requested_agent,
                    payload=creative_payload,
                )
            except Exception:
                pass

            return {
                "success": True,
                "status": "creative_media_execution_completed",
                "workflow_status": "creative_media_execution_completed",
                "execution_status": execution_status,
                "requested_agent": requested_agent,
                "tenant_id": request.tenant_id,
                "actor_role": request.actor_role,
                "owner_approved": True,
                "owner_approval_required": False,
                "provider_execution_attempted": provider_attempted_count > 0,
                "real_media_asset_count": real_media_asset_count,
                "media_asset_count": len(media_assets),
                "generation_job_count": len(generation_jobs),
                "media_pack": media_pack,
                "output": media_pack,
                "credential_values_exposed": False,
                "customer_safe": True,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "creative_media_execution_failed",
                "workflow_status": "creative_media_execution_failed",
                "execution_status": "failed",
                "requested_agent": requested_agent,
                "tenant_id": request.tenant_id,
                "error": str(exc)[:1200],
                "credential_values_exposed": False,
                "customer_safe": True,
            }
    # CREATIVE_TEAM_REAL_MEDIA_EXECUTION_PATH_END

'''

if "CREATIVE_TEAM_REAL_MEDIA_EXECUTION_PATH_START" not in text:
    if block_marker not in text:
        raise SystemExit("Run-agent insertion marker not found. No changes made.")
    text = text.replace(block_marker, creative_media_block + block_marker)

MAIN.write_text(text, encoding="utf-8")

print("RUN_AGENT_CREATIVE_MEDIA_EXECUTION_PATH_FIXED")
print("Backup:", backup_dir)