import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def request_json(path, method="GET", payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method=method,
    )

    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


summary = request_json("/admin/operations/recovery-summary")
artifacts = request_json("/admin/operations/artifacts?limit=10")
replay = request_json(
    "/admin/operations/prepare-replay",
    method="POST",
    payload={
        "tenant_id": "client_step236_001",
        "source_record_id": "record_step236_001",
        "requested_by": "owner",
    },
)
retry = request_json(
    "/admin/operations/prepare-retry",
    method="POST",
    payload={
        "tenant_id": "client_step236_001",
        "failed_execution_id": "failed_step236_001",
        "requested_by": "owner",
    },
)

combined = json.dumps({
    "summary": summary,
    "artifacts": artifacts,
    "replay": replay,
    "retry": retry,
}).lower()

checks = {
    "summary_success": summary.get("success") is True,
    "artifact_management_enabled": summary.get("artifact_management", {}).get("enabled") is True,
    "artifacts_success": artifacts.get("success") is True,
    "artifacts_list_present": isinstance(artifacts.get("artifacts"), list),
    "replay_prepared": replay.get("status") == "execution_replay_prepared",
    "replay_owner_required": replay.get("owner_approval_required") is True,
    "retry_prepared": retry.get("status") == "execution_retry_prepared",
    "retry_owner_required": retry.get("owner_approval_required") is True,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_236_OPERATIONAL_RECOVERY_ARTIFACTS_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "summary": summary,
        "artifacts": artifacts,
        "replay": replay,
        "retry": retry,
    }, indent=2))
    raise SystemExit(1)

print("STEP_236_OPERATIONAL_RECOVERY_ARTIFACTS_LOCK_OK")
