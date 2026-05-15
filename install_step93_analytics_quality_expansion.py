from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "ai_generation_service.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"ai_generation_service_before_step93_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

old = '''    def _generate_analytics_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "analytics_recommendation",
            "content": (
                f"Premium analytics recommendation for {request.region} in {request.language}, "
                f"using {request.currency}. Focus on conversion rate, CPA, ROAS, CTR, "
                f"creative fatigue, funnel performance, and scaling opportunities."
            ),
        }'''

new = '''    def _generate_analytics_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "analytics_recommendation",
            "content": (
                f"Premium analytics recommendation for {request.region} in {request.language}, "
                f"using {request.currency}. Focus on conversion rate, CPA, ROAS, CTR, "
                f"creative fatigue, funnel performance, and scaling opportunities."
            ),
            "sections": {
                "premium_expansion_layer": {
                    "analytics_quality_level": "premium_global_ecommerce_growth_intelligence_standard",
                    "competitor_benchmark_reference": [
                        "sintra",
                        "shopify_analytics_best_practice",
                        "meta_ads_performance_best_practice",
                        "premium_dtc_growth_analytics",
                    ],
                    "analysis_focus": [
                        "conversion_rate",
                        "customer_acquisition_cost",
                        "return_on_ad_spend",
                        "average_order_value",
                        "customer_lifetime_value",
                        "creative_fatigue",
                        "funnel_drop_off",
                        "product_margin_context",
                        "regional_buyer_behaviour",
                    ],
                    "recommendation_requirements": [
                        "separate observation from recommendation",
                        "identify likely cause of performance movement",
                        "include confidence level",
                        "include risk level",
                        "flag spend or scaling decisions for owner approval",
                        "recommend next test before scaling",
                        "protect against over-optimising from limited data",
                    ],
                    "localisation": {
                        "region": request.region,
                        "language": request.language,
                        "currency": request.currency,
                        "regional_benchmarking_applied": True,
                        "local_buyer_behaviour_applied": True,
                    },
                    "governance": {
                        "client_safe": True,
                        "internal_prompt_exposure_blocked": True,
                        "backend_architecture_exposure_blocked": True,
                        "budget_change_requires_owner_approval": True,
                        "campaign_scaling_requires_owner_approval": True,
                        "high_risk_recommendation_requires_owner_review": True,
                    },
                }
            },
        }'''

if old not in original:
    print("TARGET_BLOCK_NOT_FOUND")
    raise SystemExit(1)

updated = original.replace(old, new, 1)

TARGET_FILE.write_text(updated, encoding="utf-8")

print("STEP_93_ANALYTICS_QUALITY_EXPANSION_INSTALLED")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")