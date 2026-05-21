import json
import requests

BASE = "http://127.0.0.1:8000"

HEADERS = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
    "Content-Type": "application/json",
}

payload = {
    "tenant_id": "client_demo_001",
    "objective": (
        "Create a premium ecommerce launch campaign for a skincare brand. "
        "Include product copy, UGC creator brief, social content, email campaign, "
        "SEO keywords, CRM follow-up actions, analytics reporting, and a plan to "
        "increase spend only after owner approval."
    ),
    "requested_agents": [
        "strategist_agent",
        "marketing_specialist_agent",
        "product_copywriting_agent",
        "ugc_creative_agent",
        "social_media_manager_agent",
        "seo_agent",
        "email_reply_agent",
        "crm_ai_agent",
        "analytics_optimisation_agent"
    ],
    "requested_actions": [
        "create_campaign",
        "prepare_content",
        "increase_spend"
    ]
}

r = requests.post(
    BASE + "/admin/orchestration/create-plan",
    headers=HEADERS,
    json=payload,
    timeout=30,
)

print("HTTP", r.status_code)
print(json.dumps(r.json(), indent=2)[:8000])

data = r.json()
graph = data.get("dependency_graph", [])
validation = data.get("no_overlap_role_validation", [])

checks = {
    "http_200": r.status_code == 200,
    "success_true": data.get("success") is True,
    "profile_correct": data.get("orchestration_profile") == "priority6_multi_agent_orchestration_runtime_v1",
    "multi_agent_plan_created": int(data.get("agent_count", 0)) >= 5,
    "dependency_graph_created": isinstance(graph, list) and len(graph) >= 5,
    "dependencies_present": any(step.get("dependencies") for step in graph[1:]),
    "owner_approval_required": data.get("owner_approval_required") is True,
    "head_agent_separated": data.get("head_agent_not_same_as_orchestration_agent") is True,
    "orchestration_internal_only": data.get("orchestration_agent_internal_coordination_only") is True,
    "no_overlap_validated": all(v.get("overlap_status") == "role_isolated" for v in validation),
    "queue_worker_compatible": data.get("queue_worker_compatible") is True,
    "provider_direct_execution_disabled": data.get("provider_direct_execution_enabled") is False,
    "governance_bypass_false": data.get("governance_bypass") is False,
    "entitlement_bypass_false": data.get("entitlement_bypass") is False,
}

print("\n=== PRIORITY6_ORCHESTRATION_PLAN_TEST_RESULTS ===")
for key, value in checks.items():
    print(key, value)

if all(checks.values()):
    print("PRIORITY6_ORCHESTRATION_PLAN_TEST_OK")
else:
    print("PRIORITY6_ORCHESTRATION_PLAN_TEST_NEEDS_REVIEW")