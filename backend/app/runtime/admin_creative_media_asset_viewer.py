from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.app.runtime.asset_storage_signed_delivery_runtime import create_signed_asset_delivery_packet


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


def _safe_asset(asset: Dict[str, Any]) -> Dict[str, Any]:
    asset_id = str(asset.get("asset_id") or "").strip()
    provider = asset.get("provider") or asset.get("provider_key") or "internal"
    asset_type = asset.get("asset_type") or asset.get("media_type") or "creative_asset"
    playable = bool(asset.get("playable") or (asset.get("preview_ready") and not asset.get("metadata_only")))
    downloadable = bool(asset.get("download_ready") and playable)
    raw_status = str(asset.get("status") or asset.get("asset_status") or "persisted")
    if playable:
        delivery_status = "final_asset_ready"
        delivery_reason = "playable_delivery_source_available"
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

    original_preview_url = asset.get("preview_url") or asset.get("provider_asset_url") or asset.get("asset_url") or asset.get("media_url") or ""
    original_download_url = asset.get("download_url") or asset.get("provider_asset_url") or asset.get("asset_url") or asset.get("media_url") or original_preview_url or ""

    preview_url = gateway_preview_url if playable else ""
    download_url = gateway_download_url if downloadable else ""

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
        "content": asset.get("content"),
        "summary": asset.get("summary"),
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

        registry = get_persisted_creative_assets(limit=max(int(limit or 50), 1))
        raw_assets = registry.get("assets", []) if isinstance(registry, dict) else []

        jobs_result = list_media_jobs(limit=max(int(limit or 50), 1))
        jobs = jobs_result.get("jobs", [])
        jobs_by_id = {
            str(job.get("job_id") or job.get("media_job_id") or ""): job
            for job in jobs
            if isinstance(job, dict)
        }

        assets: List[Dict[str, Any]] = []
        job_evidence = []
        for asset in raw_assets:
            if not isinstance(asset, dict):
                continue
            job_id = _asset_media_job_id(asset)
            if _is_creative_media_queue_asset(asset) and job_id in jobs_by_id:
                evidence = media_job_to_visible_asset_evidence(jobs_by_id[job_id], audience="admin")
                assets.append(evidence)
                continue
            assets.append(_safe_asset(asset))

        existing_ids = {str(asset.get("asset_id") or "") for asset in assets}
        for job in jobs:
            if not isinstance(job, dict):
                continue
            evidence = media_job_to_visible_asset_evidence(job, audience="admin")
            if evidence.get("asset_id") and str(evidence.get("asset_id")) not in existing_ids:
                job_evidence.append(evidence)
                existing_ids.add(str(evidence.get("asset_id")))

        visible_assets = (assets + job_evidence)[: max(int(limit or 50), 1)]

        return {
            "success": True,
            "layer": "admin_creative_media_asset_viewer",
            "status": "ready",
            "source": "creative_asset_persistence_bridge",
            "delivery_mode": "signed_backend_asset_gateway",
            "asset_count": len(visible_assets),
            "total_asset_count": (registry.get("total_asset_count", len(assets)) if isinstance(registry, dict) else len(assets)) + len(job_evidence),
            "job_evidence_count": len(job_evidence),
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
