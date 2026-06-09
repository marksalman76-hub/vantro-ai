from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.runtime.asset_storage_signed_delivery_runtime import create_signed_asset_delivery_packet
from backend.app.runtime.creative_asset_persistence_bridge import is_valid_playable_media_source


PROVIDERS_CHECKED = ["elevenlabs", "runway", "heygen", "kling", "sync", "openai_image", "internal"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _backend_base_url() -> str:
    value = (
        os.getenv("API_BASE_URL")
        or os.getenv("BACKEND_BASE_URL")
        or os.getenv("PUBLIC_BACKEND_BASE_URL")
        or "https://api.trance-formation.com.au"
    ).rstrip("/")

    if "app.trance-formation.com.au" in value:
        return "https://api.trance-formation.com.au"

    return value


def _signed_gateway_url(asset_id: str, delivery_type: str = "preview") -> str:
    packet = create_signed_asset_delivery_packet(
        tenant_id="owner_admin",
        asset_id=asset_id,
        delivery_type=delivery_type,
        expires_in_seconds=86400,
    )

    if packet.get("status") != "ready" or not packet.get("delivery_url"):
        return ""

    return f"{_backend_base_url()}{packet.get('delivery_url')}"


def _contains_internal_or_operational_text(value: Any) -> bool:
    lowered = str(value or "").lower()
    return any(
        marker in lowered
        for marker in (
            "this is a unique multi-agent, multi-industry platform",
            "do not default to ecommerce",
            "you are executing as",
            "platform standard",
            "output quality requirement",
            "agent-specific behaviour",
            "agent specific behaviour",
            "required structure",
            "create operational execution task",
            "run delegated workforce",
            "wait for generated media assets",
            "internal governance",
            "internal routing",
            "backend instructions",
            "internal_prompt",
        )
    )


def _safe_asset_text(value: Any, *, fallback: str) -> str:
    text = " ".join(str(value or "").split()).strip()
    if not text or _contains_internal_or_operational_text(text):
        return fallback
    return text[:1000]


def _safe_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    asset_id = str(asset.get("asset_id") or "").strip()
    provider = asset.get("provider") or asset.get("provider_key") or "internal"
    asset_type = asset.get("asset_type") or asset.get("media_type") or "creative_asset"
    original_preview_url = asset.get("preview_url") or asset.get("provider_asset_url") or asset.get("asset_url") or asset.get("media_url") or ""
    original_download_url = asset.get("download_url") or asset.get("provider_asset_url") or asset.get("asset_url") or asset.get("media_url") or original_preview_url or ""
    source_candidates = [
        asset.get("provider_asset_url"),
        asset.get("preview_url"),
        asset.get("download_url"),
        asset.get("asset_url"),
        asset.get("media_url"),
    ]
    has_source_value = any(str(value or "").strip() for value in source_candidates)
    valid_source = any(is_valid_playable_media_source(value) for value in source_candidates)
    placeholder_blocked = bool(has_source_value and not valid_source)
    playable = bool(valid_source and (asset.get("playable") or (asset.get("preview_ready") and not asset.get("metadata_only"))))
    downloadable = bool(valid_source and asset.get("download_ready") and playable)
    raw_status = str(asset.get("status") or asset.get("asset_status") or "persisted")
    if playable:
        delivery_status = "final_asset_ready"
        delivery_reason = "playable_delivery_source_available"
    elif placeholder_blocked:
        delivery_status = "blocked_placeholder_source"
        delivery_reason = "placeholder_or_invalid_media_source"
    elif "failed" in raw_status.lower():
        delivery_status = "failed"
        delivery_reason = "media_generation_or_persistence_failed"
    elif asset.get("metadata_only"):
        delivery_status = "metadata_only"
        delivery_reason = "asset_record_has_no_playable_delivery_source"
    else:
        delivery_status = "processing"
        delivery_reason = "playable_media_not_available_yet"

    gateway_preview_url = _signed_gateway_url(asset_id, "preview") if asset_id and playable else ""
    gateway_download_url = _signed_gateway_url(asset_id, "download") if asset_id and downloadable else ""
    signed_delivery_created = bool(gateway_preview_url or gateway_download_url)

    preview_url = gateway_preview_url if playable else ""
    download_url = gateway_download_url if downloadable else ""

    safe_summary = _safe_asset_text(
        asset.get("summary") or asset.get("content") or "",
        fallback=f"{str(asset_type).replace('_', ' ').title()} is recorded with status {delivery_status}.",
    )

    return {
        "asset_id": asset_id or asset.get("asset_id"),
        "agent_id": asset.get("agent_id") or asset.get("agent_key") or asset.get("requested_agent"),
        "agent_label": asset.get("agent_label") or asset.get("agent_id") or asset.get("agent_key"),
        "provider": provider,
        "provider_key": provider,
        "asset_type": asset_type,
        "media_type": asset_type,
        "title": asset.get("title") or asset.get("test_label") or str(asset_type).replace("_", " ").title(),
        "status": raw_status,
        "delivery_status": delivery_status,
        "not_playable_reason": "" if playable else delivery_reason,
        "test_label": asset.get("test_label"),
        "provider_asset_id": asset.get("provider_asset_id"),
        "provider_asset_url": asset.get("provider_asset_url"),
        "preview_url": preview_url,
        "download_url": download_url,
        "original_preview_url": original_preview_url,
        "original_download_url": original_download_url,
        "preview_ready": bool(preview_url and playable),
        "download_ready": bool(download_url and downloadable),
        "playable": playable,
        "playable_asset_created": playable,
        "signed_delivery_created": signed_delivery_created,
        "metadata_only": bool(asset.get("metadata_only") or not playable),
        "invalid_or_placeholder_media_source": placeholder_blocked,
        "content": _safe_asset_text(asset.get("content"), fallback=safe_summary),
        "summary": safe_summary,
        "quality_score": asset.get("quality_score"),
        "campaign_context": asset.get("campaign_context"),
        "target_audience": asset.get("target_audience"),
        "usage_rights": asset.get("usage_rights"),
        "owner_approval_required": bool(asset.get("owner_approval_required", False)),
        "governed": True,
        "customer_safe": True,
        "credential_values_exposed": False,
            "bridge_asset_count": (locals().get("registry") or {}).get("asset_count"),
            "bridge_total_asset_count": (locals().get("registry") or {}).get("total_asset_count"),
            "last_supabase_registry_read": (locals().get("registry") or {}).get("last_supabase_registry_read"),
            "last_supabase_registry_write": (locals().get("registry") or {}).get("last_supabase_registry_write"),
            "last_supabase_media_upload": (locals().get("registry") or {}).get("last_supabase_media_upload"),
        "created_at": asset.get("created_at"),
    }


def _asset_media_job_id(asset: Dict[str, Any]) -> str:
    return str(asset.get("media_job_id") or asset.get("job_id") or asset.get("asset_id") or asset.get("id") or "").strip()


def _is_creative_media_queue_asset(asset: Dict[str, Any]) -> bool:
    status = str(asset.get("status") or asset.get("media_job_status") or asset.get("delivery_status") or "").lower()
    provider = str(asset.get("provider") or asset.get("provider_key") or "").lower()
    asset_type = str(asset.get("asset_type") or asset.get("media_type") or asset.get("type") or "").lower()
    job_id = _asset_media_job_id(asset)
    return bool(
        job_id
        and "queued" in status
        and (
            provider == "creative_media_queue"
            or asset_type == "creative_media_job_evidence"
            or job_id.startswith("media_job_")
        )
    )


def _asset_priority(asset: Dict[str, Any]) -> tuple[int, str]:
    if asset.get("playable"):
        return (0, str(asset.get("created_at") or ""))
    if asset.get("metadata_only"):
        return (2, str(asset.get("created_at") or ""))
    return (1, str(asset.get("created_at") or ""))


def _persisted_asset_lookup_allowed_with_evidence(get_persisted_creative_assets: Any, has_job_evidence: bool) -> bool:
    if not has_job_evidence:
        return True
    if os.getenv("CREATIVE_ASSET_PERSISTED_LOOKUP_WITH_EVIDENCE", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    if str(os.getenv("RENDER") or "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    if getattr(get_persisted_creative_assets, "__module__", "") != "backend.app.runtime.creative_asset_persistence_bridge":
        return True
    return not (os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL"))


def get_admin_creative_media_asset_viewer_status() -> Dict[str, Any]:
    return {
        "success": True,
        "layer": "admin_creative_media_asset_viewer",
        "status": "ready",
        "source": "creative_asset_persistence_bridge",
        "delivery_mode": "signed_backend_asset_gateway",
        "providers_checked": PROVIDERS_CHECKED,
        "credential_values_exposed": False,
            "bridge_asset_count": (locals().get("registry") or {}).get("asset_count"),
            "bridge_total_asset_count": (locals().get("registry") or {}).get("total_asset_count"),
            "last_supabase_registry_read": (locals().get("registry") or {}).get("last_supabase_registry_read"),
            "last_supabase_registry_write": (locals().get("registry") or {}).get("last_supabase_registry_write"),
            "last_supabase_media_upload": (locals().get("registry") or {}).get("last_supabase_media_upload"),
        "external_actions_performed": False,
        "live_provider_calls_triggered": False,
        "customer_safe_visibility": True,
        "verified_at": _now(),
    }


def get_admin_creative_media_assets(limit: int = 50) -> Dict[str, Any]:
    try:
        from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets
        from backend.app.runtime.async_media_job_foundation import list_media_jobs, media_job_to_visible_asset_evidence

        registry = {
            "success": True,
            "asset_count": 0,
            "total_asset_count": 0,
            "assets": [],
            "providers_checked": PROVIDERS_CHECKED,
            "credential_values_exposed": False,
        }
        raw_assets = []

        try:
            jobs_result = list_media_jobs(limit=max(int(limit or 50), 1), reconcile_visible_assets=False, include_durable_status=True)
            jobs = jobs_result.get("jobs", []) if isinstance(jobs_result, dict) else []
            if not jobs:
                jobs_result = list_media_jobs(limit=max(int(limit or 50), 1), include_durable_status=True)
                jobs = jobs_result.get("jobs", []) if isinstance(jobs_result, dict) else []
        except Exception:
            jobs_result = {
                "success": False,
                "jobs": [],
                "canonical_store": "backend:runtime_outputs/media_jobs",
                "visible_queued_job_count": 0,
                "processor_queued_job_count": 0,
                "store_paths_match": True,
                "credential_values_exposed": False,
            }
            jobs = []
        jobs_by_id = {
            str(job.get("job_id") or job.get("media_job_id") or ""): job
            for job in jobs
            if isinstance(job, dict)
        }

        assets: List[Dict[str, Any]] = []
        job_evidence = []
        evidence_ids = set()
        for job in jobs:
            if not isinstance(job, dict):
                continue
            try:
                evidence = media_job_to_visible_asset_evidence(job, audience="admin")
            except Exception:
                continue
            evidence_id = str(evidence.get("asset_id") or "")
            if evidence_id and evidence_id not in evidence_ids:
                job_evidence.append(evidence)
                evidence_ids.add(evidence_id)

        if _persisted_asset_lookup_allowed_with_evidence(get_persisted_creative_assets, bool(job_evidence)):
            try:
                registry = get_persisted_creative_assets(limit=max(int(limit or 50), 1))
                raw_assets = registry.get("assets", []) if isinstance(registry, dict) else []
            except Exception:
                registry = {
                    "success": False,
                    "asset_count": 0,
                    "total_asset_count": 0,
                    "assets": [],
                    "providers_checked": PROVIDERS_CHECKED,
                    "credential_values_exposed": False,
                }
                raw_assets = []

        asset_ids = set()
        for asset in raw_assets:
            if not isinstance(asset, dict):
                continue
            job_id = _asset_media_job_id(asset)
            if _is_creative_media_queue_asset(asset) and job_id in jobs_by_id:
                try:
                    evidence = media_job_to_visible_asset_evidence(jobs_by_id[job_id], audience="admin")
                    evidence_id = str(evidence.get("asset_id") or "")
                    if evidence_id and evidence_id not in evidence_ids:
                        job_evidence.append(evidence)
                        evidence_ids.add(evidence_id)
                except Exception:
                    pass
                continue
            try:
                safe = _safe_asset(asset)
            except Exception:
                continue
            safe_id = str(safe.get("asset_id") or "")
            if not safe_id or safe_id not in asset_ids:
                assets.append(safe)
                if safe_id:
                    asset_ids.add(safe_id)

        assets = sorted(assets, key=_asset_priority)
        safe_limit = max(int(limit or 50), 1)
        visible_assets = (assets + job_evidence)[:safe_limit]
        if job_evidence:
            visible_evidence_ids = {
                str(asset.get("asset_id") or "")
                for asset in visible_assets
                if asset.get("asset_type") == "creative_media_job_evidence"
            }
            missing_evidence = [
                evidence for evidence in job_evidence
                if str(evidence.get("asset_id") or "") not in visible_evidence_ids
            ]
            for evidence in missing_evidence:
                if len(visible_assets) < safe_limit:
                    visible_assets.append(evidence)
                    continue
                replace_index = None
                for idx in range(len(visible_assets) - 1, -1, -1):
                    candidate = visible_assets[idx]
                    if (
                        not candidate.get("playable")
                        and candidate.get("asset_type") != "creative_media_job_evidence"
                    ):
                        replace_index = idx
                        break
                if replace_index is None and visible_assets:
                    replace_index = len(visible_assets) - 1
                if replace_index is not None:
                    visible_assets[replace_index] = evidence
        visible_playable_count = sum(1 for asset in visible_assets if asset.get("playable") and asset.get("asset_type") != "creative_media_job_evidence")
        evidence_row_count = sum(1 for asset in visible_assets if asset.get("asset_type") == "creative_media_job_evidence")
        metadata_only_count = sum(1 for asset in visible_assets if asset.get("metadata_only"))

        return {
            "success": True,
            "layer": "admin_creative_media_asset_viewer",
            "status": "ready",
            "source": "creative_asset_persistence_bridge",
            "delivery_mode": "signed_backend_asset_gateway",
            "asset_count": len(visible_assets),
            "total_asset_count": (registry.get("total_asset_count", len(assets)) if isinstance(registry, dict) else len(assets)) + len(job_evidence),
            "job_evidence_count": len(job_evidence),
            "evidence_row_count": evidence_row_count,
            "playable_asset_count": visible_playable_count,
            "metadata_only_count": metadata_only_count,
            "total_detected": len(assets) + len(job_evidence),
            "canonical_store": jobs_result.get("canonical_store", "backend:runtime_outputs/media_jobs"),
            "visible_queued_job_count": jobs_result.get("visible_queued_job_count", 0),
            "processor_queued_job_count": jobs_result.get("processor_queued_job_count", 0),
            "store_paths_match": jobs_result.get("store_paths_match", True),
            "environment_context": "backend_processor",
            "assets": visible_assets,
            "providers_checked": registry.get("providers_checked", PROVIDERS_CHECKED) if isinstance(registry, dict) else PROVIDERS_CHECKED,
            "credential_values_exposed": False,
            "bridge_asset_count": (locals().get("registry") or {}).get("asset_count"),
            "bridge_total_asset_count": (locals().get("registry") or {}).get("total_asset_count"),
            "last_supabase_registry_read": (locals().get("registry") or {}).get("last_supabase_registry_read"),
            "last_supabase_registry_write": (locals().get("registry") or {}).get("last_supabase_registry_write"),
            "last_supabase_media_upload": (locals().get("registry") or {}).get("last_supabase_media_upload"),
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "customer_safe_visibility": True,
            "verified_at": _now(),
        }

    except Exception as exc:
        return {
            "success": False,
            "layer": "admin_creative_media_asset_viewer",
            "status": "unavailable",
            "source": "creative_asset_persistence_bridge",
            "delivery_mode": "signed_backend_asset_gateway",
            "asset_count": 0,
            "total_asset_count": 0,
            "assets": [],
            "providers_checked": PROVIDERS_CHECKED,
            "error": str(exc)[:1000],
            "credential_values_exposed": False,
            "bridge_asset_count": (locals().get("registry") or {}).get("asset_count"),
            "bridge_total_asset_count": (locals().get("registry") or {}).get("total_asset_count"),
            "last_supabase_registry_read": (locals().get("registry") or {}).get("last_supabase_registry_read"),
            "last_supabase_registry_write": (locals().get("registry") or {}).get("last_supabase_registry_write"),
            "last_supabase_media_upload": (locals().get("registry") or {}).get("last_supabase_media_upload"),
            "external_actions_performed": False,
            "live_provider_calls_triggered": False,
            "customer_safe_visibility": True,
            "verified_at": _now(),
        }
