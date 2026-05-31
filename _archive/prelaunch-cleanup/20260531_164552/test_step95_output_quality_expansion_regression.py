from backend.app.core.ai_generation_service import AIGenerationService, GenerationRequest


service = AIGenerationService()

cases = [
    {
        "name": "product_page",
        "requested_agent": "product_copywriting_agent",
        "workflow_stage": "store_creation",
        "task": "Create product page for Glow Serum targeting women 25 to 40 in Dubai.",
        "quality_key": "storefront_quality_level",
        "expected": "premium_global_ecommerce_standard",
    },
    {
        "name": "ugc",
        "requested_agent": "ugc_creative_agent",
        "workflow_stage": "content_generation",
        "task": "Create UGC video brief for Glow Serum targeting women 25 to 40 in Dubai.",
        "quality_key": "ugc_quality_level",
        "expected": "premium_global_ugc_ad_standard",
    },
    {
        "name": "product_image",
        "requested_agent": "product_image_agent",
        "workflow_stage": "creative_generation",
        "task": "Create premium product images for Glow Serum targeting women 25 to 40 in Dubai.",
        "quality_key": "image_quality_level",
        "expected": "premium_global_ecommerce_visual_standard",
    },
    {
        "name": "influencer",
        "requested_agent": "influencer_collaboration_agent",
        "workflow_stage": "creator_strategy",
        "task": "Create influencer collaboration strategy for Glow Serum targeting women 25 to 40 in Dubai.",
        "quality_key": "influencer_quality_level",
        "expected": "premium_global_creator_partnership_standard",
    },
    {
        "name": "analytics",
        "requested_agent": "analytics_optimisation_agent",
        "workflow_stage": "growth_analysis",
        "task": "Analyse ecommerce performance for Glow Serum targeting women 25 to 40 in Dubai.",
        "quality_key": "analytics_quality_level",
        "expected": "premium_global_ecommerce_growth_intelligence_standard",
    },
    {
        "name": "general",
        "requested_agent": "general_ecommerce_agent",
        "workflow_stage": "general_strategy",
        "task": "Create ecommerce growth recommendations for Glow Serum targeting women 25 to 40 in Dubai.",
        "quality_key": "general_quality_level",
        "expected": "premium_global_ecommerce_agent_standard",
    },
]

failed = []

print("STEP_95_OUTPUT_QUALITY_EXPANSION_REGRESSION_RESULTS")

for case in cases:
    result = service.generate(
        GenerationRequest(
            tenant_id="client_demo_001",
            requested_agent=case["requested_agent"],
            workflow_stage=case["workflow_stage"],
            task=case["task"],
            region="United Arab Emirates",
            language="Arabic",
            currency="AED",
        )
    )

    premium = result["sections"]["premium_expansion_layer"]

    checks = {
        "client_safe": result["client_safe"] is True,
        "quality_key_present": case["quality_key"] in premium,
        "quality_value_correct": premium.get(case["quality_key"]) == case["expected"],
        "localisation_region_correct": premium["localisation"]["region"] == "United Arab Emirates",
        "governance_client_safe": premium["governance"]["client_safe"] is True,
        "internal_prompt_blocked": premium["governance"]["internal_prompt_exposure_blocked"] is True,
        "backend_architecture_blocked": premium["governance"]["backend_architecture_exposure_blocked"] is True,
        "llm_routing_present": "llm_routing" in result,
        "provider_execution_present": "provider_execution" in result,
        "governance_protection_present": "governance_protection" in result,
    }

    case_failed = [name for name, passed in checks.items() if not passed]

    print(case["name"])
    print(" output_type:", result["output_type"])
    print(" quality:", premium.get(case["quality_key"]))
    print(" failed:", case_failed)

    if case_failed:
        failed.append({case["name"]: case_failed})

if failed:
    print("FAILED_CASES:", failed)
    raise SystemExit(1)

print("STEP_95_OUTPUT_QUALITY_EXPANSION_REGRESSION_OK")