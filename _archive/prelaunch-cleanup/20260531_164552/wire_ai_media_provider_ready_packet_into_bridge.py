from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
bridge_file = ROOT / "backend" / "app" / "runtime" / "provider_connector_registry.py"

if not bridge_file.exists():
    raise SystemExit("provider_connector_registry.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"provider_connector_registry_before_ai_media_provider_ready_packet_{timestamp}.py"
backup_file.write_text(bridge_file.read_text(encoding="utf-8"), encoding="utf-8")

content = bridge_file.read_text(encoding="utf-8")

HELPER_BLOCK = r'''

def extract_ai_media_provider_ready_packet(payload):
    if not isinstance(payload, dict):
        return None

    if isinstance(payload.get("provider_ready_execution_packet"), dict):
        return payload.get("provider_ready_execution_packet")

    orchestration_packet = payload.get("orchestration_packet")
    if isinstance(orchestration_packet, dict):
        packet = orchestration_packet.get("provider_ready_execution_packet")
        if isinstance(packet, dict):
            return packet

    creative_direction = payload.get("creative_direction")
    if isinstance(creative_direction, dict):
        nested_orchestration = creative_direction.get("orchestration_packet")
        if isinstance(nested_orchestration, dict):
            packet = nested_orchestration.get("provider_ready_execution_packet")
            if isinstance(packet, dict):
                return packet

    return None


def enrich_provider_payload_with_ai_media_packet(payload):
    if not isinstance(payload, dict):
        return payload

    provider_ready_packet = extract_ai_media_provider_ready_packet(payload)

    if not provider_ready_packet:
        return payload

    enriched = dict(payload)
    enriched["ai_media_provider_ready_packet"] = provider_ready_packet
    enriched["provider_payload_enriched"] = True
    enriched["provider_packet_type"] = provider_ready_packet.get("packet_type")
    enriched["provider_execution_allowed"] = provider_ready_packet.get("execution_allowed", True)
    enriched["provider_manual_review_required"] = provider_ready_packet.get("manual_review_required", False)
    enriched["provider_primary_slot"] = provider_ready_packet.get("primary_provider_slot")
    enriched["provider_fallback_slots"] = provider_ready_packet.get("fallback_provider_slots", [])
    enriched["provider_parameters"] = provider_ready_packet.get("provider_parameters", {})
    enriched["provider_continuity_controls"] = provider_ready_packet.get("continuity_controls", {})
    enriched["provider_multilingual_controls"] = provider_ready_packet.get("multilingual_controls", {})
    enriched["provider_fallback_controls"] = provider_ready_packet.get("fallback_controls", {})
    enriched["provider_governance_controls"] = provider_ready_packet.get("governance_controls", {})
    enriched["provider_quality_controls"] = provider_ready_packet.get("quality_controls", {})

    return enriched
'''

if "def extract_ai_media_provider_ready_packet(" not in content:
    content = content.rstrip() + "\n" + HELPER_BLOCK + "\n"

# Safe integration: wrap known payload variables if they exist.
candidate_replacements = [
    ("payload = dict(payload)", "payload = enrich_provider_payload_with_ai_media_packet(dict(payload))"),
    ("payload=dict(payload)", "payload=enrich_provider_payload_with_ai_media_packet(dict(payload))"),
    ("execution_payload = dict(execution_payload)", "execution_payload = enrich_provider_payload_with_ai_media_packet(dict(execution_payload))"),
    ("provider_payload = dict(provider_payload)", "provider_payload = enrich_provider_payload_with_ai_media_packet(dict(provider_payload))"),
]

changed = False
for old, new in candidate_replacements:
    if old in content and new not in content:
        content = content.replace(old, new)
        changed = True

# If no known variable assignment exists, leave helper functions available.
# Existing bridge calls can import/use the helper without breaking runtime.
bridge_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_ai_media_provider_ready_packet_bridge.py"
test_file.write_text(r'''
from backend.app.runtime.provider_connector_registry import (
    extract_ai_media_provider_ready_packet,
    enrich_provider_payload_with_ai_media_packet,
)


def main():
    provider_packet = {
        "packet_type": "provider_ready_ai_media_execution_packet",
        "execution_allowed": True,
        "manual_review_required": False,
        "primary_provider_slot": "video_generation_provider",
        "fallback_provider_slots": ["ugc_avatar_provider"],
        "provider_parameters": {"aspect_ratio_priority": "9:16"},
        "continuity_controls": {"same_face_required": True},
        "multilingual_controls": {"multilingual_required": True},
        "fallback_controls": {"fallback_enabled": True},
        "governance_controls": {"do_not_publish_without_governance": True},
        "quality_controls": {"premium_only": True},
    }

    payload = {
        "creative_direction": {
            "orchestration_packet": {
                "provider_ready_execution_packet": provider_packet
            }
        }
    }

    extracted = extract_ai_media_provider_ready_packet(payload)
    assert extracted["packet_type"] == "provider_ready_ai_media_execution_packet"

    enriched = enrich_provider_payload_with_ai_media_packet(payload)
    assert enriched["provider_payload_enriched"] is True
    assert enriched["provider_packet_type"] == "provider_ready_ai_media_execution_packet"
    assert enriched["provider_execution_allowed"] is True
    assert enriched["provider_primary_slot"] == "video_generation_provider"
    assert enriched["provider_parameters"]["aspect_ratio_priority"] == "9:16"
    assert enriched["provider_continuity_controls"]["same_face_required"] is True
    assert enriched["provider_multilingual_controls"]["multilingual_required"] is True
    assert enriched["provider_governance_controls"]["do_not_publish_without_governance"] is True
    assert enriched["provider_quality_controls"]["premium_only"] is True

    unchanged = enrich_provider_payload_with_ai_media_packet({"normal": "payload"})
    assert unchanged == {"normal": "payload"}

    print("AI_MEDIA_PROVIDER_READY_PACKET_BRIDGE_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_PROVIDER_READY_PACKET_BRIDGE_WIRED")
print(f"Backup: {backup_file}")
print(f"Updated: {bridge_file}")
print(f"Created: {test_file}")