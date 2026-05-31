from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "ai_generation_service.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"ai_generation_service_before_step92_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

old = '''    def _generate_influencer_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "influencer_collaboration_strategy",
            "content": (
                f"Premium influencer collaboration strategy for {request.region} in {request.language}, "
                f"using {request.currency}. Focus on creators with authentic audience trust, "
                f"high engagement quality, commercial content quality, and strong product-category alignment. "
                f"Task: {request.task}"
            ),
        }'''

new = '''    def _generate_influencer_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "influencer_collaboration_strategy",
            "content": (
                f"Premium influencer collaboration strategy for {request.region} in {request.language}, "
                f"using {request.currency}. Focus on creators with authentic audience trust, "
                f"high engagement quality, commercial content quality, and strong product-category alignment. "
                f"Task: {request.task}"
            ),
            "sections": {
                "premium_expansion_layer": {
                    "influencer_quality_level": "premium_global_creator_partnership_standard",
                    "competitor_benchmark_reference": [
                        "sintra",
                        "ugc_creator_marketplace_best_practice",
                        "high_conversion_affiliate_campaigns",
                        "premium_dtc_creator_partnerships",
                    ],
                    "creator_scoring_focus": [
                        "audience_fit",
                        "engagement_quality",
                        "content_authenticity",
                        "regional_relevance",
                        "brand_style_alignment",
                        "conversion_potential",
                        "collaboration_risk",
                    ],
                    "collaboration_requirements": [
                        "identify creators by niche and audience match",
                        "score creators before outreach",
                        "separate gifting from paid collaborations",
                        "track usage rights and content terms",
                        "track discount codes and affiliate links",
                        "require owner approval before paid commitments",
                    ],
                    "localisation": {
                        "region": request.region,
                        "language": request.language,
                        "currency": request.currency,
                        "regional_creator_market_applied": True,
                        "local_collaboration_norms_applied": True,
                    },
                    "governance": {
                        "client_safe": True,
                        "internal_prompt_exposure_blocked": True,
                        "backend_architecture_exposure_blocked": True,
                        "paid_collaboration_requires_owner_approval": True,
                        "contract_or_usage_rights_requires_owner_approval": True,
                        "budget_commitment_requires_owner_approval": True,
                    },
                }
            },
        }'''

if old not in original:
    print("TARGET_BLOCK_NOT_FOUND")
    raise SystemExit(1)

updated = original.replace(old, new, 1)

TARGET_FILE.write_text(updated, encoding="utf-8")

print("STEP_92_INFLUENCER_QUALITY_EXPANSION_INSTALLED")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")