from backend.app.core.ai_generation_service import AIGenerationService, GenerationRequest


service = AIGenerationService()

blocked_terms = [
    "api_key",
    "secret",
    "credential value",
    "internal prompt",
    "system prompt",
    "developer prompt",
    "backend config",
    "learning internals",
    "governance internals",
    "provider secret",
]

cases = [
    ("product_copywriting_agent", "store_creation", "Create product page for Glow Serum targeting women 25 to 40 in Dubai."),
    ("ugc_creative_agent", "content_generation", "Create UGC video brief for Glow Serum targeting women 25 to 40 in Dubai."),
    ("product_image_agent", "creative_generation", "Create premium product images for Glow Serum targeting women 25 to 40 in Dubai."),
    ("influencer_collaboration_agent", "creator_strategy", "Create influencer strategy for Glow Serum targeting women 25 to 40 in Dubai."),
    ("analytics_optimisation_agent", "growth_analysis", "Analyse ecommerce performance for Glow Serum targeting women 25 to 40 in Dubai."),
    ("general_ecommerce_agent", "general_strategy", "Create ecommerce growth recommendations for Glow Serum targeting women 25 to 40 in Dubai."),
]

failed = []

print("STEP_99_CUSTOMER_SAFE_OUTPUT_SURFACE_RESULTS")

for agent, stage, task in cases:
    result = service.generate(
        GenerationRequest(
            tenant_id="client_demo_001",
            requested_agent=agent,
            workflow_stage=stage,
            task=task,
            region="United Arab Emirates",
            language="Arabic",
            currency="AED",
        )
    )

    visible_text = str({
        "output_type": result.get("output_type"),
        "content": result.get("content"),
        "sections": result.get("sections"),
    }).lower()

    unsafe_terms_found = [term for term in blocked_terms if term in visible_text]

    checks = {
        "client_safe_true": result.get("client_safe") is True,
        "has_content": bool(result.get("content")),
        "has_sections": isinstance(result.get("sections"), dict),
        "no_blocked_terms_in_visible_output": len(unsafe_terms_found) == 0,
        "governance_protection_present": "governance_protection" in result,
        "llm_routing_present": "llm_routing" in result,
        "provider_execution_present": "provider_execution" in result,
    }

    case_failed = [name for name, passed in checks.items() if not passed]

    print(agent)
    print(" output_type:", result.get("output_type"))
    print(" unsafe_terms_found:", unsafe_terms_found)
    print(" failed:", case_failed)

    if case_failed:
        failed.append({agent: case_failed, "unsafe_terms_found": unsafe_terms_found})

if failed:
    print("FAILED_CASES:", failed)
    raise SystemExit(1)

print("STEP_99_CUSTOMER_SAFE_OUTPUT_SURFACE_OK")