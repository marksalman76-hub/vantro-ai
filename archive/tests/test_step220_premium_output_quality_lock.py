import json
import urllib.request

API = "http://127.0.0.1:8000/run-agent"

payload = {
    "tenant_id": "client_step203_001",
    "requested_agent": "product_copywriting_agent",
    "workflow_stage": "store_creation",
    "action_type": "product_copy_generation",
    "actor_role": "owner",
    "owner_approved": True,
    "task": "Create premium product copy for an anti-ageing vitamin C skincare serum targeting women aged 30-55 who want brighter skin, smoother texture, premium ingredients, objection handling, emotional hooks, SEO title, meta description, conversion bullets and a high-converting CTA.",
}

req = urllib.request.Request(
    API,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-tenant-id": "client_step203_001",
        "x-actor-role": "owner",
    },
    method="POST",
)

with urllib.request.urlopen(req, timeout=30) as res:
    data = json.loads(res.read().decode("utf-8"))

output = data.get("output", {})
content = str(output.get("content", "")).lower()
sections = output.get("sections", {})
benefits = sections.get("benefits", [])
conversion_requirements = sections.get("conversion_requirements", [])

generic_bad_phrases = [
    "lorem ipsum",
    "generic product",
    "placeholder",
    "insert product",
    "basic output",
]

quality_terms = [
    "benefit",
    "trust",
    "conversion",
    "premium",
    "cta",
]

checks = {
    "success_true": data.get("success") is True,
    "execution_completed": data.get("status") == "agent_execution_completed",
    "quality_passed": data.get("quality", {}).get("passed") is True,
    "quality_score_100": data.get("quality", {}).get("score") == 100,
    "client_safe": output.get("client_safe") is True,
    "premium_output_type": output.get("output_type") == "premium_shopify_product_page",
    "content_present": len(content) > 250,
    "benefits_present": isinstance(benefits, list) and len(benefits) >= 5,
    "conversion_requirements_present": isinstance(conversion_requirements, list) and len(conversion_requirements) >= 8,
    "premium_expansion_layer_present": isinstance(sections.get("premium_expansion_layer"), dict),
    "no_generic_bad_phrases": not any(phrase in content for phrase in generic_bad_phrases),
    "commercial_quality_terms_present": all(term in content for term in quality_terms),
    "provider_safely_blocked_until_ready": output.get("provider_execution", {}).get("metadata", {}).get("live_execution_allowed") is False,
    "internal_prompt_exposure_blocked": output.get("governance_protection", {}).get("internal_prompt_exposure_blocked") is True,
    "backend_architecture_exposure_blocked": output.get("governance_protection", {}).get("backend_architecture_exposure_blocked") is True,
}

print("STEP_220_PREMIUM_OUTPUT_QUALITY_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print("OUTPUT_SUMMARY", json.dumps({
        "status": data.get("status"),
        "quality": data.get("quality"),
        "output_type": output.get("output_type"),
        "product_name": output.get("product_name"),
        "target_audience": output.get("target_audience"),
        "content_preview": content[:500],
    }, indent=2))
    raise SystemExit(1)

print("STEP_220_PREMIUM_OUTPUT_QUALITY_LOCK_OK")