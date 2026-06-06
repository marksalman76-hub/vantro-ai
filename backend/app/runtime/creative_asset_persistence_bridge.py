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
    supabase_storage_status = lambda: {"durable_storage_ready": False, "storage_provider": "local_runtime_fallback"}
    media_output_bucket = lambda: "creative-media-outputs"
    upload_file_to_supabase = None
    upload_json_to_supabase = None
    download_json_from_supabase = None

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"
REGISTRY_DIR = Path(os.getenv("CREATIVE_MEDIA_PERSISTENCE_DIR", str(DEFAULT_REGISTRY_DIR)))
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = REGISTRY_DIR / "creative_assets.json"
REGISTRY_INDEX_FILE = REGISTRY_DIR / "creative_assets_index.json"
ASSET_RECORD_DIR = REGISTRY_DIR / "assets"
ASSET_RECORD_DIR.mkdir(parents=True, exist_ok=True)
SUPABASE_REGISTRY_OBJECT_KEY = "registries/creative_media_asset_registry_index.json"

LAST_SUPABASE_REGISTRY_READ = {}
LAST_SUPABASE_REGISTRY_WRITE = {}
LAST_SUPABASE_MEDIA_UPLOAD = {}

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


def _load_local_registry():
    if REGISTRY_INDEX_FILE.exists():
        try:
            data = json.loads(REGISTRY_INDEX_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            pass

    if not REGISTRY_FILE.exists():
        return []
    try:
        data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _registry_object_key():
    return SUPABASE_REGISTRY_OBJECT_KEY


def _asset_record_object_key(asset_id):
    return f"registries/creative_media_assets/{_safe_slug(asset_id)}.json"


def _asset_record_path(asset_id):
    return ASSET_RECORD_DIR / f"{_safe_slug(asset_id)}.json"


def _load_registry():
    global LAST_SUPABASE_REGISTRY_READ

    local_data = _load_local_registry()

    if supabase_enabled() and download_json_from_supabase is not None:
        result = download_json_from_supabase(
            bucket=media_output_bucket(),
            object_key=_registry_object_key(),
            fallback=None,
        )
        LAST_SUPABASE_REGISTRY_READ = {
            "success": result.get("success"),
            "status": result.get("status"),
            "bucket": result.get("bucket"),
            "object_key": result.get("object_key"),
            "http_status": result.get("http_status"),
            "error": result.get("error"),
            "checked_at": _now(),
        }

        data = result.get("json")
        if result.get("success") and isinstance(data, list):
            return data

    return local_data


def _save_registry(index_records):
    global LAST_SUPABASE_REGISTRY_WRITE

    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    safe_index = [_lightweight_index_record(item) for item in index_records if isinstance(item, dict)]
    REGISTRY_INDEX_FILE.write_text(json.dumps(safe_index, indent=2), encoding="utf-8")

    if supabase_enabled() and upload_json_to_supabase is not None:
        result = upload_json_to_supabase(
            bucket=media_output_bucket(),
            object_key=_registry_object_key(),
            payload=safe_index,
        )
        LAST_SUPABASE_REGISTRY_WRITE = {
            "success": result.get("success"),
            "status": result.get("status"),
            "bucket": result.get("bucket"),
            "object_key": result.get("object_key"),
            "http_status": result.get("http_status"),
            "error": _truncate(result.get("error"), 500),
            "checked_at": _now(),
        }


def _safe_string(value, fallback=""):
    if value is None:
        return fallback
    return str(value)


def _safe_slug(value, fallback="asset"):
    raw = _safe_string(value, fallback).strip() or fallback
    return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in raw)[:160] or fallback


def _truncate(value, max_len=1000):
    text = _safe_string(value)
    if len(text) <= max_len:
        return text
    return text[:max_len] + "...[truncated]"


def _is_data_url(value):
    return _safe_string(value).strip().startswith("data:")


def _is_browser_safe_url(value):
    text = _safe_string(value).strip()
    if not text or _is_data_url(text) or len(text) > 2000:
        return False
    return text.startswith("http://") or text.startswith("https://")


def _first_browser_safe_url(*values):
    for value in values:
        if _is_browser_safe_url(value):
            return _safe_string(value).strip()
    return ""


def _safe_reference(value, max_len=500):
    text = _safe_string(value).strip()
    if not text:
        return ""
    if _is_data_url(text):
        return "embedded_generated_asset_reference_hidden"
    return _truncate(text, max_len)


def _safe_upload_summary(upload):
    if not isinstance(upload, dict):
        return upload
    return {
        "success": bool(upload.get("success")),
        "status": upload.get("status"),
        "bucket": upload.get("bucket"),
        "object_key": upload.get("object_key"),
        "http_status": upload.get("http_status"),
        "error": _truncate(upload.get("error"), 500),
        "public_url": upload.get("public_url") if _is_browser_safe_url(upload.get("public_url")) else None,
    }


def _lightweight_index_record(record):
    return {
        "asset_id": record.get("asset_id"),
        "agent_id": record.get("agent_id"),
        "agent_label": record.get("agent_label"),
        "provider": record.get("provider") or "internal",
        "asset_type": record.get("asset_type"),
        "title": _truncate(record.get("title"), 180),
        "test_label": _truncate(record.get("test_label"), 180),
        "provider_asset_id": _truncate(record.get("provider_asset_id"), 240),
        "provider_asset_url": _safe_reference(record.get("provider_asset_url"), 500),
        "preview_url": _safe_reference(record.get("preview_url"), 500),
        "download_url": _safe_reference(record.get("download_url"), 500),
        "original_preview_url": _safe_reference(record.get("original_preview_url"), 500),
        "original_download_url": _safe_reference(record.get("original_download_url"), 500),
        "preview_ready": bool(record.get("preview_ready")),
        "download_ready": bool(record.get("download_ready")),
        "playable": bool(record.get("playable")),
        "metadata_only": bool(record.get("metadata_only")),
        "local_file_found_for_upload": bool(record.get("local_file_found_for_upload")),
        "storage_provider": record.get("storage_provider"),
        "storage_bucket": record.get("storage_bucket"),
        "storage_object_key": record.get("storage_object_key"),
        "storage_upload": _safe_upload_summary(record.get("storage_upload")),
        "registry_partitioned": True,
        "content": _truncate(record.get("content"), 1000),
        "summary": _truncate(record.get("summary"), 1000),
        "status": record.get("status"),
        "quality_score": record.get("quality_score"),
        "campaign_context": _truncate(record.get("campaign_context"), 1000),
        "target_audience": _truncate(record.get("target_audience"), 500),
        "usage_rights": _truncate(record.get("usage_rights"), 500),
        "owner_approval_required": bool(record.get("owner_approval_required", False)),
        "governed": True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": record.get("created_at"),
    }


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


def _candidate_local_path(packet):
    for key in [
        "composed_video_path",
        "final_synced_video_path",
        "audio_path",
        "video_path",
        "download_url",
        "preview_url",
        "provider_asset_url",
    ]:
        value = packet.get(key)
        if not value:
            continue
        text = str(value)
        if text.startswith("http://") or text.startswith("https://"):
            continue
        path = Path(text)
        if path.exists() and path.is_file():
            return path
    return None


def _maybe_upload_media_file(packet, asset_id, asset_type):
    global LAST_SUPABASE_MEDIA_UPLOAD

    if not supabase_enabled() or upload_file_to_supabase is None:
        LAST_SUPABASE_MEDIA_UPLOAD = {
            "success": False,
            "status": "supabase_not_configured",
            "checked_at": _now(),
        }
        return None

    path = _candidate_local_path(packet)
    if path is None:
        LAST_SUPABASE_MEDIA_UPLOAD = {
            "success": False,
            "status": "local_file_not_found_for_upload",
            "candidate_keys_checked": [
                "composed_video_path",
                "final_synced_video_path",
                "audio_path",
                "video_path",
                "download_url",
                "preview_url",
                "provider_asset_url",
            ],
            "checked_at": _now(),
        }
        return LAST_SUPABASE_MEDIA_UPLOAD

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

    LAST_SUPABASE_MEDIA_UPLOAD = {
        "success": upload.get("success"),
        "status": upload.get("status"),
        "bucket": upload.get("bucket"),
        "object_key": upload.get("object_key"),
        "http_status": upload.get("http_status"),
        "error": upload.get("error"),
        "public_url": upload.get("public_url"),
        "checked_at": _now(),
    }

    return upload


def _save_asset_record(stored):
    global LAST_SUPABASE_REGISTRY_WRITE

    safe_record = _lightweight_index_record(stored)
    _asset_record_path(stored["asset_id"]).write_text(json.dumps(safe_record, indent=2), encoding="utf-8")

    if supabase_enabled() and upload_json_to_supabase is not None:
        result = upload_json_to_supabase(
            bucket=media_output_bucket(),
            object_key=_asset_record_object_key(stored["asset_id"]),
            payload=safe_record,
        )
        LAST_SUPABASE_REGISTRY_WRITE = {
            "success": result.get("success"),
            "status": result.get("status"),
            "bucket": result.get("bucket"),
            "object_key": result.get("object_key"),
            "http_status": result.get("http_status"),
            "error": _truncate(result.get("error"), 500),
            "checked_at": _now(),
        }


def persist_creative_asset(asset_packet: dict):
    registry = _load_registry()
    packet = dict(asset_packet or {})

    agent_id = packet.get("agent_id") or packet.get("agent_key") or packet.get("requested_agent")
    asset_type = classify_creative_asset(packet)
    created_at = _now()
    asset_id = packet.get("asset_id") or _asset_id(packet)

    local_path = _candidate_local_path(packet)
    storage_upload = _maybe_upload_media_file(packet, asset_id, asset_type)
    storage_url = storage_upload.get("public_url") if isinstance(storage_upload, dict) and storage_upload.get("success") else None
    provider_url = _first_browser_safe_url(
        packet.get("provider_asset_url"),
        packet.get("preview_url"),
        packet.get("download_url"),
        packet.get("asset_url"),
        packet.get("media_url"),
    )
    local_url = str(local_path) if local_path is not None else ""

    playable_url = storage_url or provider_url or local_url
    playable = bool(playable_url)
    metadata_only = not playable

    if storage_url:
        storage_provider = "supabase"
    elif provider_url:
        storage_provider = "external_provider_url"
    elif local_url:
        storage_provider = "local_runtime_file"
    else:
        storage_provider = "metadata_only"

    stored = {
        "asset_id": asset_id,
        "agent_id": agent_id,
        "agent_label": packet.get("agent_label"),
        "provider": packet.get("provider") or "internal",
        "asset_type": asset_type,
        "title": packet.get("title") or packet.get("test_label") or asset_type.replace("_", " ").title(),
        "test_label": packet.get("test_label"),
        "provider_asset_url": playable_url,
        "provider_asset_id": _truncate(packet.get("provider_asset_id"), 500),
        "preview_url": playable_url,
        "download_url": playable_url,
        "original_preview_url": _safe_reference(packet.get("preview_url") or packet.get("provider_asset_url")),
        "original_download_url": _safe_reference(packet.get("download_url") or packet.get("provider_asset_url")),
        "preview_ready": playable,
        "download_ready": playable,
        "playable": playable,
        "metadata_only": metadata_only,
        "local_file_found_for_upload": local_path is not None,
        "storage_provider": storage_provider,
        "storage_bucket": media_output_bucket() if storage_url else None,
        "storage_object_key": storage_upload.get("object_key") if isinstance(storage_upload, dict) else None,
        "storage_upload": _safe_upload_summary(storage_upload),
        "registry_partitioned": True,
        "content": _truncate(packet.get("content"), 1000),
        "summary": _truncate(packet.get("summary"), 1000),
        "status": packet.get("status") or ("persisted" if playable else "metadata_only_not_playable"),
        "quality_score": packet.get("quality_score"),
        "campaign_context": _truncate(packet.get("campaign_context"), 1000),
        "target_audience": _truncate(packet.get("target_audience"), 500),
        "usage_rights": _truncate(packet.get("usage_rights"), 500),
        "owner_approval_required": bool(packet.get("owner_approval_required", False)),
        "governed": True,
        "customer_safe": True,
        "credential_values_exposed": False,
        "created_at": created_at,
    }

    existing_ids = {item.get("asset_id") for item in registry if isinstance(item, dict)}
    if stored["asset_id"] not in existing_ids:
        registry.insert(0, _lightweight_index_record(stored))
    else:
        registry = [
            _lightweight_index_record(stored) if isinstance(item, dict) and item.get("asset_id") == stored["asset_id"] else item
            for item in registry
        ]

    registry = registry[:500]
    _save_asset_record(stored)
    _save_registry(registry)

    return {
        "success": True,
        "asset_id": stored["asset_id"],
        "asset_type": stored["asset_type"],
        "registry_count": len(registry),
        "storage_provider": stored["storage_provider"],
        "durable_storage_ready": stored["storage_provider"] == "supabase",
        "preview_ready": stored["preview_ready"],
        "download_ready": stored["download_ready"],
        "playable": stored["playable"],
        "metadata_only": stored["metadata_only"],
        "storage_upload_status": storage_upload.get("status") if isinstance(storage_upload, dict) else None,
        "storage_upload_http_status": storage_upload.get("http_status") if isinstance(storage_upload, dict) else None,
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
        "last_supabase_registry_read": LAST_SUPABASE_REGISTRY_READ,
        "last_supabase_registry_write": LAST_SUPABASE_REGISTRY_WRITE,
        "last_supabase_media_upload": LAST_SUPABASE_MEDIA_UPLOAD,
        "credential_values_exposed": False,
    }
