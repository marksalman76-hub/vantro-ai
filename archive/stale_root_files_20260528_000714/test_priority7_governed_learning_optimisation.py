import json
import requests

BASE = "http://127.0.0.1:8000"

HEADERS = {
    "x-tenant-id": "owner",
    "x-actor-role": "owner",
    "Content-Type": "application/json",
}

def get(path):
    return requests.get(BASE + path, headers=HEADERS, timeout=30)

def post(path, payload=None):
    return requests.post(BASE + path, headers=HEADERS, json=payload or {}, timeout=30)

def show(label, response):
    print("\n===", label, "===")
    print("HTTP", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2)[:7000])
    except Exception:
        print(response.text[:7000])

# 1. Readiness before scoring.
r1 = get("/admin/learning/governed-readiness")
show("LEARNING_READINESS_INITIAL", r1)

# 2. Score safe/high-quality outcome.
safe_payload = {
    "tenant_id": "client_demo_001",
    "project_id": "priority7_learning_test",
    "agent_id": "marketing_specialist_agent",
    "task_type": "premium_campaign_strategy",
    "client_context_used": True,
    "competitor_context_used": True,
    "evidence": ["client profile", "competitor positioning", "regional ecommerce context"],
    "output": (
        "Specific premium ecommerce campaign recommendation with action steps, next step sequence, "
        "region-aware positioning, currency-sensitive offer framing, audience segmentation, competitor "
        "differentiation, measurable metric targets, and practical optimisation recommendations for the "
        "client's skincare launch. The recommendation separates observation from action and keeps budget "
        "changes behind owner approval."
    )
}
r2 = post("/admin/learning/score-outcome", safe_payload)
show("SCORE_SAFE_OUTCOME", r2)

# 3. Score high-consequence outcome.
risk_payload = {
    "tenant_id": "client_demo_001",
    "project_id": "priority7_learning_test",
    "agent_id": "paid_ads_agent",
    "task_type": "paid_ads_scaling_recommendation",
    "client_context_used": True,
    "competitor_context_used": True,
    "evidence": ["performance report"],
    "output": (
        "Recommendation proposes to increase spend and scale campaign after reviewing performance. "
        "This must stay approval-gated and cannot execute without owner approval."
    ),
    "requested_action": "increase spend",
    "owner_review_required": True
}
r3 = post("/admin/learning/score-outcome", risk_payload)
show("SCORE_HIGH_CONSEQUENCE_OUTCOME", r3)

# 4. Score lower-confidence outcome.
low_confidence_payload = {
    "tenant_id": "client_demo_001",
    "project_id": "priority7_learning_test",
    "agent_id": "seo_agent",
    "task_type": "seo_recommendation",
    "client_context_used": False,
    "competitor_context_used": False,
    "uncertainty_flag": True,
    "output": "Generic SEO recommendation. TODO add details."
}
r4 = post("/admin/learning/score-outcome", low_confidence_payload)
show("SCORE_LOW_CONFIDENCE_OUTCOME", r4)

# 5. Aggregate patterns.
r5 = post("/admin/learning/aggregate-patterns", {"tenant_id": "client_demo_001"})
show("AGGREGATE_LEARNING_PATTERNS", r5)

# 6. Generate coaching.
r6 = post("/admin/learning/generate-coaching", {"tenant_id": "client_demo_001"})
show("GENERATE_AGENT_COACHING", r6)

# 7. Final readiness.
r7 = get("/admin/learning/governed-readiness")
show("LEARNING_READINESS_FINAL", r7)

d2 = r2.json()
d3 = r3.json()
d4 = r4.json()
d5 = r5.json()
d6 = r6.json()
d7 = r7.json()

safe_outcome = d2.get("outcome", {})
risk_outcome = d3.get("outcome", {})
low_outcome = d4.get("outcome", {})
pattern = d5.get("pattern", {})
coaching = d6.get("coaching", {})

checks = {
    "readiness_http_200": r1.status_code == 200 and r7.status_code == 200,
    "outcome_scoring_enabled": d7.get("outcome_scoring_enabled") is True,
    "confidence_scoring_enabled": d7.get("confidence_scoring_enabled") is True,
    "consequence_scoring_enabled": d7.get("consequence_scoring_enabled") is True,
    "safe_outcome_persisted": d2.get("outcome_persisted") is True,
    "risk_outcome_persisted": d3.get("outcome_persisted") is True,
    "low_outcome_persisted": d4.get("outcome_persisted") is True,
    "safe_quality_score_good": int(safe_outcome.get("quality_score", 0)) >= 80,
    "risk_owner_review_required": risk_outcome.get("owner_review_required") is True,
    "risk_not_approved_for_autonomous_learning": risk_outcome.get("approved_for_autonomous_learning") is False,
    "low_confidence_lower_than_safe": int(low_outcome.get("confidence_score", 100)) < int(safe_outcome.get("confidence_score", 0)),
    "patterns_persisted": d5.get("pattern_persisted") is True,
    "pattern_has_agent_performance": bool(pattern.get("agent_performance")),
    "coaching_persisted": d6.get("coaching_persisted") is True,
    "coaching_internal_only": coaching.get("internal_only") is True,
    "coaching_not_client_visible": coaching.get("client_visible") is False,
    "no_core_model_retraining": d7.get("core_model_retraining_allowed") is False,
    "no_autonomous_governance_mutation": d7.get("autonomous_governance_mutation_allowed") is False,
    "owner_controls_preserved": d7.get("owner_approval_controls_preserved") is True,
    "outcome_count_positive": int(d7.get("outcome_count", 0)) >= 3,
    "pattern_count_positive": int(d7.get("pattern_count", 0)) >= 1,
    "coaching_count_positive": int(d7.get("coaching_count", 0)) >= 1,
    "governance_bypass_false": d7.get("governance_bypass") is False,
    "entitlement_bypass_false": d7.get("entitlement_bypass") is False,
}

print("\n=== PRIORITY7_GOVERNED_LEARNING_OPTIMISATION_TEST_RESULTS ===")
for key, value in checks.items():
    print(key, value)

if all(checks.values()):
    print("PRIORITY7_GOVERNED_LEARNING_OPTIMISATION_TEST_OK")
else:
    print("PRIORITY7_GOVERNED_LEARNING_OPTIMISATION_TEST_NEEDS_REVIEW")