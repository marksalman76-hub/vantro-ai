from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "ai_generation_service.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"ai_generation_service_before_step91_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

old = '''                "quality_rejection_rules": result["quality_rejection_rules"],
            },
        }'''

new = '''                "quality_rejection_rules": result["quality_rejection_rules"],
                "premium_expansion_layer": {
                    "image_quality_level": "premium_global_ecommerce_visual_standard",
                    "competitor_benchmark_reference": [
                        "higgsfield",
                        "shopify_plus_dtc_brands",
                        "premium_meta_ad_creatives",
                        "top_tiktok_shop_product_visuals",
                    ],
                    "optimisation_focus": [
                        "conversion_ready_composition",
                        "premium_lighting",
                        "mobile_first_framing",
                        "clear_product_visibility",
                        "trust_and_quality_perception",
                        "platform_native_adaptability",
                        "realistic_commercial_photography",
                    ],
                    "visual_requirements": [
                        "product_must_be_clearly_identifiable",
                        "lighting_must_feel_premium_and_realistic",
                        "background_must_support_but_not_distract",
                        "composition_must_work_for_square_vertical_and_landscape_formats",
                        "avoid_plastic_or_ai_generated_texture",
                        "include_ad_ready_crop_guidance",
                    ],
                    "localisation": {
                        "region": request.region,
                        "language": request.language,
                        "currency": request.currency,
                        "regional_visual_style_applied": True,
                        "local_buyer_expectations_applied": True,
                    },
                    "governance": {
                        "client_safe": True,
                        "internal_prompt_exposure_blocked": True,
                        "backend_architecture_exposure_blocked": True,
                        "brand_usage_requires_client_approval": True,
                    },
                },
            },
        }'''

if old not in original:
    print("TARGET_BLOCK_NOT_FOUND")
    raise SystemExit(1)

updated = original.replace(old, new, 1)

TARGET_FILE.write_text(updated, encoding="utf-8")

print("STEP_91_PRODUCT_IMAGE_QUALITY_EXPANSION_INSTALLED")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")