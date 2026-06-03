from pathlib import Path

checks = {
    "frontend/src/lib/adminClientExecutionVisibilitySync.ts": [
        "buildAdminClientExecutionVisibilityPacket",
        "admin_client_execution_visibility_sync_enabled",
        "credential_values_exposed: false",
        "owner_visibility",
        "synced_sections",
    ],
    "frontend/src/app/api/client-execution-visibility-sync/route.ts": [
        "buildAdminClientExecutionVisibilityPacket",
        "client",
        "cache-control",
    ],
    "frontend/src/app/api/admin-client-execution-visibility-sync/route.ts": [
        "Admin authorisation required",
        "buildAdminClientExecutionVisibilityPacket",
        "admin",
        "tenant_key",
    ],
    "frontend/src/app/api/client-execution-matrix/route.ts": [
        "admin_client_execution_visibility_sync_enabled",
        "visibility_sync",
        "buildAdminClientExecutionVisibilityPacket",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW12_ADMIN_CLIENT_EXECUTION_VISIBILITY_SYNC_FAILED missing={missing}")

print("ROW12_ADMIN_CLIENT_EXECUTION_VISIBILITY_SYNC_PASSED")
