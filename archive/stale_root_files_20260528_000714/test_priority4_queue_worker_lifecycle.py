import json
import requests

BASE = "http://127.0.0.1:8000"

HEADERS = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
    "Content-Type": "application/json",
}

QUEUE_PAYLOAD = {
    "tenant_id": "client_demo_001",
    "project_id": "priority4_worker_lifecycle_test",
    "agent_id": "marketing_specialist_agent",
    "action_type": "safe_worker_lifecycle_validation",
    "payload": {
        "task": "Validate queue worker lifecycle without direct provider execution.",
        "governance_required": True,
        "owner_approval_controls_preserved": True
    },
    "priority": 5,
    "max_retries": 2
}

def post(path, payload):
    return requests.post(BASE + path, headers=HEADERS, json=payload, timeout=30)

def get(path):
    return requests.get(BASE + path, headers=HEADERS, timeout=30)

def show(label, response):
    print("\n===", label, "===")
    print("HTTP", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2)[:5000])
    except Exception:
        print(response.text[:5000])

# 1. Check queue readiness.
r1 = get("/admin/execution-queue/readiness")
show("QUEUE_READINESS", r1)

# 2. Enqueue test item.
r2 = post("/admin/execution-queue/enqueue", QUEUE_PAYLOAD)
show("QUEUE_ENQUEUE", r2)

enqueue_data = r2.json()
queue_id = enqueue_data.get("queue_id") or enqueue_data.get("id")

# 3. Confirm queued item appears.
r3 = get("/admin/execution-queue?tenant_id=client_demo_001&status=queued&limit=10")
show("QUEUE_LIST_QUEUED", r3)

# 4. Claim batch.
r4 = post("/admin/execution-queue/claim-batch", {"limit": 3})
show("QUEUE_CLAIM_BATCH", r4)

# 5. Run worker once.
r5 = post("/admin/execution-queue/run-worker-once", {"limit": 3})
show("QUEUE_RUN_WORKER_ONCE", r5)

# 6. Check worker health after processing.
r6 = get("/admin/execution-queue/worker-health")
show("QUEUE_WORKER_HEALTH_AFTER_RUN", r6)

data1 = r1.json()
data2 = r2.json()
data4 = r4.json()
data5 = r5.json()
data6 = r6.json()

checks = {
    "queue_readiness_http_200": r1.status_code == 200,
    "queue_ready_true": data1.get("queue_ready") is True or data1.get("success") is True,
    "enqueue_success": data2.get("success") is True,
    "queue_id_created": bool(queue_id),
    "claim_route_success": data4.get("success") is True,
    "worker_run_success": data5.get("success") is True,
    "worker_profile_correct": data5.get("worker_profile") == "priority4_execution_queue_worker_v1",
    "governed_execution_required": data5.get("governed_execution_required") is True,
    "provider_direct_execution_disabled": data5.get("provider_direct_execution_enabled") is False,
    "owner_controls_preserved": data5.get("owner_approval_controls_preserved") is True,
    "worker_health_success": data6.get("success") is True,
    "worker_batches_incremented": int(data6.get("state", {}).get("total_batches", 0)) >= 1,
    "governance_bypass_false": data6.get("governance_bypass") is False,
    "entitlement_bypass_false": data6.get("entitlement_bypass") is False,
}

print("\n=== PRIORITY4_QUEUE_WORKER_LIFECYCLE_TEST_RESULTS ===")
print("queue_id", queue_id)
for key, value in checks.items():
    print(key, value)

if all(checks.values()):
    print("PRIORITY4_QUEUE_WORKER_LIFECYCLE_TEST_OK")
else:
    print("PRIORITY4_QUEUE_WORKER_LIFECYCLE_TEST_NEEDS_REVIEW")