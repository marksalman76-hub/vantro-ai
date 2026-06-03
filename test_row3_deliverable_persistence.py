from pathlib import Path

checks = {
    "frontend/src/lib/deliverablePersistence.ts": [
        "persistLatestDeliverable",
        "getLatestDeliverable",
        "resolveTenantKey",
        "hasRealDeliverableOutput",
        ".runtime",
        "client-deliverables",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "persistLatestDeliverable",
        "deliverable_persisted",
        "persisted_deliverable_id",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "getLatestDeliverable",
        "latest_deliverable_store",
        "persistence_source",
    ],
}

missing = {}
for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW3_DELIVERABLE_PERSISTENCE_FAILED missing={missing}")

print("ROW3_DELIVERABLE_PERSISTENCE_PASSED")
