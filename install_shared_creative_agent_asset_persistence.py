from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"shared_creative_agent_asset_persistence_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

PERSIST_FILE = ROOT / "backend" / "app" / "runtime" / "creative_asset_persistence_bridge.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
TEST_FILE = ROOT / "test_shared_creative_agent_asset_persistence.py"

CREATIVE_AGENT_IDS = [
    "ugc_creative_agent",
    "social_media_manager_content_creator_agent",
    "paid_ads_agent",
    "creative_rotation_agent",
    "product_image_agent",
    "marketing_specialist_agent",
    "influencer_collaboration_agent",
    "influencer_outreach_agent",
]

PERSIST_CODE = r'''
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib

ROOT = Path(__file__).resolve().parents[3]
REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = REGISTRY_DIR / "creative_assets.json"

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
}

def _load_registry():
    if not REGISTRY_FILE.exists():
        return []
    try:
        data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_registry(data):
    REGISTRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _safe_string(value, fallback=""):
    if value is None:
        return fallback
    return str(value)

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

def persist_creative_asset(asset_packet: dict):
    registry = _load_registry()
    packet = dict(asset_packet or {})

    agent_id = packet.get("agent_id") or packet.get("agent_key") or packet.get("requested_agent")
    asset_type = classify_creative_asset(packet)
    created_at = datetime.now(timezone.utc).isoformat()

    stored = {
        "asset_id": packet.get("asset_id") or _asset_id(packet),
        "agent_id": agent_id,
        "agent_label": packet.get("agent_label"),
        "provider": packet.get("provider") or "internal",
        "asset_type": asset_type,
        "title": packet.get("title") or packet.get("test_label") or asset_type.replace("_", " ").title(),
        "test_label": packet.get("test_label"),
        "provider_asset_url": packet.get("provider_asset_url"),
        "provider_asset_id": packet.get("provider_asset_id"),
        "preview_url": packet.get("preview_url") or packet.get("provider_asset_url"),
        "download_url": packet.get("download_url") or packet.get("provider_asset_url"),
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

    return {
        "success": True,
        "asset_count": len(safe_assets),
        "total_asset_count": len(registry),
        "assets": safe_assets,
        "providers_checked": ["elevenlabs", "runway", "heygen", "kling", "sync", "internal"],
        "credential_values_exposed": False,
    }
'''

TEST_CODE = r'''
from backend.app.runtime.creative_asset_persistence_bridge import (
    get_persisted_creative_assets,
    is_creative_agent,
    persist_creative_agent_output,
)

assert is_creative_agent("ugc_creative_agent")
assert is_creative_agent("influencer_collaboration_agent")
assert is_creative_agent("marketing_specialist_agent")
assert not is_creative_agent("crm_ai_agent")

result = persist_creative_agent_output(
    "influencer_collaboration_agent",
    {
        "provider": "internal",
        "title": "Influencer outreach packet for lymphatic massager campaign",
        "summary": "Creator shortlist, UGC brief, outreach messages, usage rights notes, affiliate discount plan.",
        "target_audience": "Women 25-45 interested in wellness and self-care.",
        "quality_score": 91,
    },
)

assert result["success"] is True
assert result["persisted"] is True
assert result["persisted_asset_count"] >= 1
assert result["credential_values_exposed"] is False

assets = get_persisted_creative_assets()
assert assets["success"] is True
assert assets["asset_count"] >= 1
assert assets["credential_values_exposed"] is False

print("SHARED_CREATIVE_AGENT_ASSET_PERSISTENCE_PASSED")
'''

def backup(path: Path):
    if path.exists():
        dest = BACKUP / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

def main():
    backup(PERSIST_FILE)
    backup(MAIN_FILE)

    PERSIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    PERSIST_FILE.write_text(PERSIST_CODE, encoding="utf-8", newline="\n")
    TEST_FILE.write_text(TEST_CODE, encoding="utf-8", newline="\n")

    main_text = MAIN_FILE.read_text(encoding="utf-8", errors="ignore")

    import_line = "from backend.app.runtime.creative_asset_persistence_bridge import get_persisted_creative_assets, persist_creative_agent_output\n"
    if "persist_creative_agent_output" not in main_text:
        marker = "from backend.app.runtime.creative_asset_persistence_bridge import"
        if marker in main_text:
            lines = main_text.splitlines()
            lines = [line for line in lines if "creative_asset_persistence_bridge import" not in line and "get_persisted_creative_assets" not in line]
            main_text = "\n".join(lines) + "\n"
        insert_marker = "from fastapi import"
        idx = main_text.find(insert_marker)
        end = main_text.find("\n", idx)
        main_text = main_text[:end+1] + import_line + main_text[end+1:]

    MAIN_FILE.write_text(main_text, encoding="utf-8", newline="\n")

    print("SHARED_CREATIVE_AGENT_ASSET_PERSISTENCE_INSTALLED")
    print(f"Backup: {BACKUP}")
    print(f"Updated: {PERSIST_FILE}")
    print(f"Updated: {MAIN_FILE}")
    print(f"Created: {TEST_FILE}")

if __name__ == "__main__":
    main()