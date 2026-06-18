from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
component = ROOT / "frontend" / "src" / "components" / "ClientCreateMediaProductionCard.tsx"

client_text = client_page.read_text(encoding="utf-8", errors="ignore")
component_text = component.read_text(encoding="utf-8", errors="ignore") if component.exists() else ""

required_component_phrases = [
    "Create Media",
    "Create media and manage outputs",
    "No human/avatar",
    "Generate new avatar/person",
    "Use uploaded face/likeness",
    "Use saved brand spokesperson/avatar",
    "queued, processing, completed, or failed",
]

proof = {
    "isolated_client_media_card_attempted": True,
    "isolated_client_media_card_passed": True,
    "component_exists": component.exists(),
    "component_imported_by_client_page": "ClientCreateMediaProductionCard" in client_text,
    "component_mounted_in_client_page": "<ClientCreateMediaProductionCard" in client_text,
    "open_button_bridge_present": "data-client-create-media-open-button" in component_text,
    "request_panel_present": "data-client-create-media-request-panel" in component_text and "Submit media request soon" in component_text,
    "use_client_first_line_client_page": client_text.splitlines()[0].strip() == '"use client";',
    "use_client_first_line_component": component_text.splitlines()[0].strip() == '"use client";' if component_text else False,
    "required_component_phrases_present": {phrase: phrase in component_text for phrase in required_component_phrases},
    "provider_names_hidden_from_component": all(
        name not in component_text.lower()
        for name in ["kling", "runway", "heygen", "sync", "elevenlabs", "ffmpeg"]
    ),
    "provider_call_attempted": False,
    "media_generation_attempted": False,
    "billing_mutation_attempted": False,
    "credit_mutation_attempted": False,
    "stripe_live_charge_attempted": False,
    "aws21_or_later_work_attempted": False,
    "public_cutover_enabled": False,
    "next_operator_action": "review_client_create_media_card_in_browser",
}

proof["isolated_client_media_card_passed"] = (
    proof["component_exists"]
    and proof["component_imported_by_client_page"]
    and proof["component_mounted_in_client_page"]
    and proof["use_client_first_line_client_page"]
    and proof["use_client_first_line_component"]
    and proof["open_button_bridge_present"]
    and proof["request_panel_present"]
    and all(proof["required_component_phrases_present"].values())
    and proof["provider_names_hidden_from_component"]
)

print("ISOLATED_CLIENT_MEDIA_CARD_PROOF:")
print(json.dumps(proof, indent=2, sort_keys=True))

if not proof["isolated_client_media_card_passed"]:
    raise SystemExit("ISOLATED_CLIENT_MEDIA_CARD_FAILED")

print("ISOLATED_CLIENT_MEDIA_CARD_PASSED")
