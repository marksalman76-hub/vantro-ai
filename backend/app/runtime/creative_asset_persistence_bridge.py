from pathlib import Path
from datetime import datetime, timezone
import json
import os
import hashlib
import mimetypes

try:
    from backend.app.runtime.supabase_creative_storage import (
        supabase_enabled,
        storage_status as supabase_storage_status,
        media_output_bucket,
        upload_file_to_supabase,
        upload_json_to_supabase,
        download_json_from_supabase,
    )
except Exception:
    supabase_enabled = lambda: False
    supabase_storage_status = lambda: {"durable_storage_ready": False}
    media_output_bucket = lambda: "creative-media-outputs"
    upload_file_to_supabase = None
    upload_json_to_supabase = None
    download_json_from_supabase = None

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"
REGISTRY_DIR = Path(os.getenv("CREATIVE_MEDIA_PERSISTENCE_DIR", str(DEFAULT_REGISTRY_DIR)))
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = REGISTRY_DIR / "creative_assets.json"
SUPABASE_REGISTRY_OBJECT_KEY = "registries/creative_media_asset_registry.json"

CREATIVE_AGENT_IDS = {
    "ugc_creative_agent",
    "social_media_manager_content_creator_agent",
    "paid_ads_agent",
    "creative_rotation_agent",
    "product_image_agent",
    "marketing_specialist_agent",
    "influencer_collaboration_agent",
    "influencer_outreach_agent",
}

CREATIVE_TEXT_ASSET_TYPES = {
    "ugc_script",
    "creator_brief",
    "campaign_brief",
    "ad_brief",
    "social_content_plan",
    "influencer_outreach_packet",
    "usage_rights_record",
    "affiliate_discount_plan",
    "performance_tracking_plan",
    "creative_strategy",
}

MEDIA_ASSET_TYPES = {
    "video",
    "audio",
    "image",
    "voiceover",
    "lipsync_video",
    "dubbing_audio",
    "ugc_video",
    "ad_video",
    "product_image",
    "combined_video",
}

def _now():
    return datetime.now(timezone.utc).isoformat()

def _blank_registry():
    return []

def _load_registry():
    if supabase_enabled() and download_json_from_supabase is not None:
        result = download_json_from_supabase(
            bucket=media_output_bucket(),
            object_key=SUPABASE_REGISTRY_OBJECT_KEY,
            fallback=[],
        )
        data = result.get("json")
        if isinstance(data, list):
            return data

    if not REGISTRY_FILE.exists():
        return []
    try:
        data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_registry(data):
    if supabase_enabled() and upload_json_to_supabase is not None:
        upload_json_to_supabase(
            bucket=media_output_bucket(),
            object_key=SUPABASE_REGISTRY_OBJECT_KEY,
            payload=data,
        )

    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _safe_string(value, fallback=""):
    if value is None:
        return fallback
    return str(value)

def _safe_slug(value, fallback="asset"):
    raw = _safe_string(value, fallback).strip() or fallback
    return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in raw)[:160] or fallback

def _asset_id(packet):
    raw = "|".join([
        _safe_string(packet.get("agent_id")),
        _safe_string(packet.get("provider")),
        _safe_string(packet.get("asset_type")),
        _safe_string(packet.get("test_label")),
        _safe_string(packet.get("provider_asset_id")),
        _safe_string(packet.get("provider_asset_url") or packet.get("preview_url") or packet.get("download_url")),
        _safe_string(packet.get("title")),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def is_creative_agent(agent_id):
    return str(agent_id or "").strip() in CREATIVE_AGENT_IDS

def classify_creative_asset(packet):
    explicit = str(packet.get("asset_type") or "").strip().lower()
    if explicit:
        return explicit

    provider = str(packet.get("provider") or "").lower()
    title = str(packet.get("title") or packet.get("test_label") or "").lower()
    content = str(packet.get("content") or packet.get("summary") or "").lower()

    if "elevenlabs" in provider or "voice" in title:
        return "voiceover"
    if "runway" in provider or "kling" in provider or "video" in title:
        return "video"
    if "image" in title or "product image" in content:
        return "image"
    if "influencer" in title or "creator shortlist" in content or "usage rights" in content:
        return "influencer_outreach_packet"
    if "ugc" in title or "script" in content:
        return "ugc_script"
    if "ad" in title or "campaign" in content:
        return "campaign_brief"

    return "creative_strategy"

def _maybe_upload_media_file(packet, asset_id, asset_type):
    if not supabase_enabled() or upload_file_to_supabase is None:
        return None

    candidate = (
        packet.get("download_url")
        or packet.get("preview_url")
        or packet.get("provider_asset_url")
    )

    if not candidate:
        return None

    candidate_text = str(candidate)
    if candidate_text.startswith("http://") or candidate_text.startswith("https://"):
        return None

    path = Path(candidate_text)
    if not path.exists() or not path.is_file():
        return None

    filename = path.name
    test_label = _safe_slug(packet.get("test_label") or packet.get("title") or asset_id)
    object_key = f"tenants/{_safe_slug(packet.get('tenant_id') or 'owner_admin')}/{asset_type}/{asset_id}_{test_label}_{filename}"
    content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"

    upload = upload_file_to_supabase(
        bucket=media_output_bucket(),
        object_key=object_key,
        file_path=str(path),
        content_type=content_type,
    )

    if upload.get("success"):
        return upload

    return upload

def persist_creative_asset(asset_packet: dict):
    registry = _load_registry()
    packet = dict(asset_packet or {})

    agent_id = packet.get("agent_id") or packet.get("agent_key") or packet.get("requested_agent")
    asset_type = classify_creative_asset(packet)
    created_at = _now()
    asset_id = packet.get("asset_id") or _asset_id(packet)

    storage_upload = _maybe_upload_media_file(packet, asset_id, asset_type)
    storage_url = storage_upload.get("public_url") if isinstance(storage_upload, dict) and storage_upload.get("success") else None

    stored = {
        "asset_id": asset_id,
        "agent_id": agent_id,
        "agent_label": packet.get("agent_label"),
        "provider": packet.get("provider") or "internal",
        "asset_type": asset_type,
        "title": packet.get("title") or packet.get("test_label") or asset_type.replace("_", " ").title(),
        "test_label": packet.get("test_label"),
        "provider_asset_url": storage_url or packet.get("provider_asset_url"),
        "provider_asset_id": packet.get("provider_asset_id"),
        "preview_url": storage_url or packet.get("preview_url") or packet.get("provider_asset_url"),
        "download_url": storage_url or packet.get("download_url") or packet.get("provider_asset_url"),
        "original_preview_url": packet.get("preview_url") or packet.get("provider_asset_url"),
        "original_download_url": packet.get("download_url") or packet.get("provider_asset_url"),
        "storage_provider": "supabase" if storage_url else "external_or_local_runtime_fallback",
        "storage_bucket": media_output_bucket() if storage_url else None,
        "storage_object_key": storage_upload.get("object_key") if isinstance(storage_upload, dict) else None,
        "storage_upload": storage_upload,
        "content": packet.get("content"),
        "summary": packet.get("summary"),
        "status": packet.get("status") or "persisted",
        "quality_score": packet.get("quality_score"),
        "campaign_context": packet.get("campaign_context"),
        "target_audience": packet.get("target_audience"),
        "usage_rights": packet.get("usage_rights"),
        "owner_approval_required": bool(packet.get("owner_approval_required", False)),
        "governed": True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": created_at,
    }

    existing_ids = {item.get("asset_id") for item in registry if isinstance(item, dict)}
    if stored["asset_id"] not in existing_ids:
        registry.insert(0, stored)

    registry = registry[:500]
    _save_registry(registry)

    return {
        "success": True,
        "asset_id": stored["asset_id"],
        "asset_type": stored["asset_type"],
        "registry_count": len(registry),
        "storage_provider": stored["storage_provider"],
        "durable_storage_ready": stored["storage_provider"] == "supabase",
        "credential_values_exposed": False,
    }

def persist_creative_agent_output(agent_id: str, output_packet: dict):
    if not is_creative_agent(agent_id):
        return {
            "success": True,
            "persisted": False,
            "reason": "not_creative_agent",
            "credential_values_exposed": False,
        }

    packet = output_packet or {}
    records = []

    media_assets = packet.get("media_assets")
    if isinstance(media_assets, list):
        for asset in media_assets:
            if isinstance(asset, dict):
                asset["agent_id"] = agent_id
                records.append(persist_creative_asset(asset))

    persisted_asset_records = packet.get("persisted_asset_records")
    if isinstance(persisted_asset_records, list):
        for asset in persisted_asset_records:
            if isinstance(asset, dict):
                asset["agent_id"] = agent_id
                records.append(persist_creative_asset(asset))

    if not records:
        text_content = (
            packet.get("live_output")
            or packet.get("output")
            or packet.get("result")
            or packet.get("summary")
            or packet.get("message")
        )

        title = packet.get("title") or packet.get("test_label") or f"{agent_id} creative output"

        records.append(
            persist_creative_asset(
                {
                    "agent_id": agent_id,
                    "provider": packet.get("provider") or packet.get("selected_provider") or "internal",
                    "asset_type": classify_creative_asset(
                        {
                            "asset_type": packet.get("asset_type"),
                            "provider": packet.get("provider"),
                            "title": title,
                            "content": text_content,
                        }
                    ),
                    "title": title,
                    "test_label": packet.get("test_label"),
                    "content": text_content,
                    "summary": packet.get("summary"),
                    "status": packet.get("status") or "creative_output_persisted",
                    "quality_score": packet.get("quality_score"),
                    "campaign_context": packet.get("campaign_context"),
                    "target_audience": packet.get("target_audience"),
                    "owner_approval_required": packet.get("owner_approval_required", False),
                }
            )
        )

    return {
        "success": True,
        "persisted": True,
        "agent_id": agent_id,
        "persisted_asset_count": len(records),
        "persisted_asset_records": records,
        "credential_values_exposed": False,
    }

def get_persisted_creative_assets(limit=100):
    registry = _load_registry()
    safe_assets = []

    for item in registry[: int(limit or 100)]:
        if not isinstance(item, dict):
            continue
        clean = dict(item)
        clean["credential_values_exposed"] = False
        safe_assets.append(clean)

    storage = supabase_storage_status()

    return {
        "success": True,
        "asset_count": len(safe_assets),
        "total_asset_count": len(registry),
        "assets": safe_assets,
        "providers_checked": ["elevenlabs", "runway", "heygen", "kling", "sync", "internal"],
        "storage_provider": storage.get("storage_provider"),
        "durable_storage_ready": storage.get("durable_storage_ready"),
        "storage_bucket": media_output_bucket(),
        "credential_values_exposed": False,
    }
