import json
import requests

BASE = "http://127.0.0.1:8000"

HEADERS = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
    "Content-Type": "application/json",
}

PLAN_ID = "orch_priority6_state_memory_test_001"

def get(path):
    return requests.get(BASE + path, headers=HEADERS, timeout=30)

def post(path, payload):
    return requests.post(BASE + path, headers=HEADERS, json=payload, timeout=30)

def show(label, response):
    print("\n===", label, "===")
    print("HTTP", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2)[:5000])
    except Exception:
        print(response.text[:5000])

# 1. Record orchestration start state.
r1 = post("/admin/orchestration/record-state", {
    "plan_id": PLAN_ID,
    "tenant_id": "client_demo_001",
    "event_type": "orchestration_started",
    "status": "started",
    "step_id": "step_1_strategist_agent",
    "agent_id": "strategist_agent",
    "dependency_status": {},
    "parallel_group": "strategy_group",
    "head_agent_review_required": True,
    "data": {
        "objective": "Validate orchestration state persistence, cross-agent result memory, and recovery continuation."
    }
})
show("RECORD_STATE_STARTED", r1)

# 2. Record strategist result memory.
r2 = post("/admin/orchestration/record-result", {
    "plan_id": PLAN_ID,
    "tenant_id": "client_demo_001",
    "step_id": "step_1_strategist_agent",
    "agent_id": "strategist_agent",
    "result_type": "strategy_output",
    "result_summary": "Strategist produced the campaign direction, buyer angle, offer structure, and risk guardrails.",
    "result_payload": {
        "campaign_direction": "premium skincare launch",
        "buyer_angle": "sensitive skin trust and visible results",
        "next_agents": ["marketing_specialist_agent", "product_copywriting_agent"],
        "owner_approval_required_for_spend": True
    },
    "head_agent_review_required": True
})
show("RECORD_RESULT_STRATEGIST", r2)

# 3. Record next step completed.
r3 = post("/admin/orchestration/record-state", {
    "plan_id": PLAN_ID,
    "tenant_id": "client_demo_001",
    "event_type": "orchestration_step_completed",
    "status": "completed",
    "step_id": "step_1_strategist_agent",
    "agent_id": "strategist_agent",
    "dependency_status": {
        "step_1_strategist_agent": "completed"
    },
    "parallel_group": "strategy_group",
    "head_agent_review_required": True,
    "data": {
        "result_memory_available": True,
        "next_step_ready": "step_2_marketing_specialist_agent"
    }
})
show("RECORD_STATE_COMPLETED", r3)

# 4. Fetch context.
r4 = get(f"/admin/orchestration/context/{PLAN_ID}")
show("ORCHESTRATION_CONTEXT", r4)

# 5. Fetch recovery packet.
r5 = get(f"/admin/orchestration/recovery/{PLAN_ID}")
show("ORCHESTRATION_RECOVERY", r5)

# 6. Confirm readiness counts.
r6 = get("/admin/orchestration/state-readiness")
show("STATE_READINESS_AFTER_RECORDING", r6)

d1 = r1.json()
d2 = r2.json()
d4 = r4.json()
d5 = r5.json()
d6 = r6.json()

checks = {
    "record_state_success": d1.get("success") is True,
    "record_result_success": d2.get("success") is True,
    "context_success": d4.get("success") is True,
    "recovery_success": d5.get("success") is True,
    "state_log_exists": d6.get("state_log_exists") is True,
    "result_memory_exists": d6.get("result_memory_exists") is True,
    "state_event_count_positive": int(d6.get("state_event_count", 0)) >= 2,
    "result_memory_count_positive": int(d6.get("result_memory_count", 0)) >= 1,
    "cross_agent_context_available": d4.get("cross_agent_context_available") is True,
    "recovery_context_available": d4.get("recovery_context_available") is True,
    "recovery_ready": d5.get("recovery_ready") is True,
    "head_agent_review_ready": d5.get("head_agent_review_ready") is True,
    "parallel_safe_resume_ready": d5.get("parallel_safe_resume_ready") is True,
    "governance_bypass_false": d5.get("governance_bypass") is False,
    "entitlement_bypass_false": d5.get("entitlement_bypass") is False,
}

print("\n=== PRIORITY6_ORCHESTRATION_STATE_RUNTIME_TEST_RESULTS ===")
for key, value in checks.items():
    print(key, value)

if all(checks.values()):
    print("PRIORITY6_ORCHESTRATION_STATE_RUNTIME_TEST_OK")
else:
    print("PRIORITY6_ORCHESTRATION_STATE_RUNTIME_TEST_NEEDS_REVIEW")