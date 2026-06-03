from pathlib import Path

checks = {
    "frontend/src/lib/realMediaGenerationProviders.ts": [
        "getRealMediaProviderRegistry",
        "selectRealMediaProvider",
        "inferMediaCapability",
        "attachRealMediaProviderDecision",
        "Runway",
        "Kling",
        "HeyGen",
        "ElevenLabs",
        "Replicate",
        "OpenAI",
        "live_external_call_executed: false",
        "external_action_performed: false",
    ],
    "frontend/src/app/api/real-media-generation-providers/route.ts": [
        "real_media_generation_providers_enabled",
        "getRealMediaProviderRegistry",
        "selectRealMediaProvider",
        "live_external_call_executed",
    ],
    "frontend/src/app/api/admin-real-media-generation-providers/route.ts": [
        "credential_values_exposed: false",
        "Admin authorisation required",
        "real_media_generation_providers_enabled",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "attachRealMediaProviderDecision",
        "realMediaGenerationProviders",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW8_REAL_MEDIA_GENERATION_PROVIDERS_FAILED missing={missing}")

print("ROW8_REAL_MEDIA_GENERATION_PROVIDERS_PASSED")
