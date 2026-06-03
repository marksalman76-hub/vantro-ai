from pathlib import Path

checks = {
    "frontend/src/lib/durableRuntimeStorage.ts": [
        "DURABLE_RUNTIME_STORAGE_ROOT",
        "DURABLE_RUNTIME_STORE_PATHS",
        "ensureDurableRuntimeStorage",
        "durableReadJson",
        "durableWriteJson",
        "buildDurableRuntimeStorageStatus",
        "durable_runtime_storage_enabled",
        "credential_values_exposed: false",
    ],
    "frontend/src/app/api/durable-runtime-storage-status/route.ts": [
        "buildDurableRuntimeStorageStatus",
        "cache-control",
    ],
    "frontend/src/app/api/admin-durable-runtime-storage-status/route.ts": [
        "Admin authorisation required",
        "buildDurableRuntimeStorageStatus",
        "owner_visibility",
    ],
    "frontend/src/lib/deliverablePersistence.ts": ["durable_runtime_storage_enabled"],
    "frontend/src/lib/approvalRevisionHistory.ts": ["durable_runtime_storage_enabled"],
    "frontend/src/lib/businessProfilePersistence.ts": ["durable_runtime_storage_enabled"],
    "frontend/src/lib/executionStateSync.ts": ["durable_runtime_storage_enabled"],
    "frontend/src/lib/mediaAssetLifecycle.ts": ["durable_runtime_storage_enabled"],
    "frontend/src/lib/providerQueueRetryFailover.ts": ["durable_runtime_storage_enabled"],
    "frontend/src/lib/billingStripeSubscriptions.ts": ["durable_runtime_storage_enabled"],
    "frontend/src/lib/packageCreditEnforcement.ts": ["durable_runtime_storage_enabled"],
}

missing = {}

for file, needles in checks.items():
    path = Path(file)
    if not path.exists():
        missing[file] = ["FILE_MISSING"]
        continue
    text = path.read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW15_DURABLE_RUNTIME_STORAGE_FAILED missing={missing}")

print("ROW15_DURABLE_RUNTIME_STORAGE_PASSED")
