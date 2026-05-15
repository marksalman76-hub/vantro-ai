from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "ai_generation_service.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"ai_generation_service_before_step90_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

old = '''                "provider_execution_packet": result["provider_execution_packet"],
            },
        }'''

new = '''                "provider_execution_packet": result["provider_execution_packet"],
                "premium_expansion_layer": {
                    "ugc_quality_level": "premium_global_ugc_ad_standard",
                    "competitor_benchmark_reference": [
                        "higgsfield",
                        "sintra",
                        "top_performing_tiktok_shop_creatives",
                        "high_conversion_meta_reels_ads",
                    ],
                    "optimisation_focus": [
                        "hook_strength",
                        "creator_authenticity",
                        "scroll_stopping_opening",
                        "product_believability",
                        "native_platform_feel",
                        "clear_conversion_intent",
                        "audio_visual_realism",
                    ],
                    "creative_requirements": [
                        "first_three_seconds_must_create_curiosity",
                        "creator_delivery_must_feel_unscripted",
                        "product_benefit_must_be_visible_or_demonstrated",
                        "avoid_overproduced_ad_language",
                        "include_platform_native_caption_direction",
                        "include objection-handling angle",
                    ],
                    "localisation": {
                        "region": request.region,
                        "language": request.language,
                        "currency": request.currency,
                        "local_creator_style_applied": True,
                        "regional_buyer_psychology_applied": True,
                    },
                    "governance": {
                        "client_safe": True,
                        "internal_prompt_exposure_blocked": True,
                        "backend_architecture_exposure_blocked": True,
                        "paid_collaboration_requires_owner_approval": True,
                    },
                },
            },
        }'''

if old not in original:
    print("TARGET_BLOCK_NOT_FOUND")
    raise SystemExit(1)

updated = original.replace(old, new, 1)

TARGET_FILE.write_text(updated, encoding="utf-8")

print("STEP_90_UGC_QUALITY_EXPANSION_INSTALLED")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")