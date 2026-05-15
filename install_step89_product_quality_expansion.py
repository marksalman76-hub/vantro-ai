from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "ai_generation_service.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"ai_generation_service_before_step89_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

old = '''        return {
            "client_safe": True,
            "output_type": "premium_shopify_product_page",
            "product_name": product_name,
            "target_audience": target_audience,
            "content": html,
            "sections": {
                "headline": product_name,
                "target_audience": target_audience,
                "benefits": [
                    "Benefit-led product positioning",
                    "Trust-building ecommerce copy",
                    "Conversion-focused offer structure",
                ],
                "conversion_requirements": [
                    "Clear above-the-fold value proposition",
                    "Benefit-first bullet points",
                    "Objection handling",
                    "FAQ-ready structure",
                    "Strong call-to-action",
                ],
            },
        }'''

new = '''        return {
            "client_safe": True,
            "output_type": "premium_shopify_product_page",
            "product_name": product_name,
            "target_audience": target_audience,
            "content": html,
            "sections": {
                "headline": product_name,
                "target_audience": target_audience,
                "benefits": [
                    "Benefit-led product positioning",
                    "Trust-building ecommerce copy",
                    "Conversion-focused offer structure",
                    "Region-aware buying psychology adaptation",
                    "Mobile-first ecommerce optimisation",
                    "Premium perceived value positioning",
                ],
                "conversion_requirements": [
                    "Clear above-the-fold value proposition",
                    "Benefit-first bullet points",
                    "Objection handling",
                    "FAQ-ready structure",
                    "Strong call-to-action",
                    "Trust badge positioning",
                    "Social proof placement",
                    "Mobile conversion optimisation",
                    "Checkout friction reduction",
                    "Platform-native ecommerce structure",
                ],
                "premium_expansion_layer": {
                    "storefront_quality_level": "premium_global_ecommerce_standard",
                    "competitor_benchmark_reference": [
                        "10web",
                        "base44",
                        "shopify_plus",
                        "high_conversion_dtc_brands",
                    ],
                    "optimisation_focus": [
                        "conversion_rate",
                        "trust_building",
                        "visual_hierarchy",
                        "buyer_confidence",
                        "mobile_performance",
                        "platform_native_structure",
                    ],
                    "localisation": {
                        "region": request.region,
                        "language": request.language,
                        "currency": request.currency,
                        "local_buyer_psychology_applied": True,
                    },
                    "governance": {
                        "client_safe": True,
                        "internal_prompt_exposure_blocked": True,
                        "backend_architecture_exposure_blocked": True,
                    },
                },
            },
        }'''

if old not in original:
    print("TARGET_BLOCK_NOT_FOUND")
    raise SystemExit(1)

updated = original.replace(old, new)

TARGET_FILE.write_text(updated, encoding="utf-8")

print("STEP_89_PRODUCT_QUALITY_EXPANSION_INSTALLED")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")