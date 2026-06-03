from pathlib import Path

checks = {
    "frontend/src/lib/businessProfilePersistence.ts": [
        "persistBusinessProfile",
        "getBusinessProfile",
        "normaliseBusinessProfile",
        "business-profiles",
        "profile_completed",
        "Your business",
    ],
    "frontend/src/app/api/client-business-profile/route.ts": [
        "business_profile_persisted",
        "business_profile_store",
        "persistBusinessProfile",
        "getBusinessProfile",
        "profile_completed",
    ],
}

optional_checks = {
    "frontend/src/app/api/client-me/route.ts": [
        "business_profile_persisted",
        "getBusinessProfile",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

for file, needles in optional_checks.items():
    p = Path(file)
    if p.exists():
        text = p.read_text(encoding="utf-8")
        absent = [needle for needle in needles if needle not in text]
        if absent:
            missing[file] = absent

if missing:
    raise SystemExit(f"ROW5_BUSINESS_PROFILE_PERSISTENCE_FAILED missing={missing}")

print("ROW5_BUSINESS_PROFILE_PERSISTENCE_PASSED")
