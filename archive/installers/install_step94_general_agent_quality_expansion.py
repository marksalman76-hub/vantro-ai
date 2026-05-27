from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "ai_generation_service.py"

BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = BACKUP_DIR / f"ai_generation_service_before_step94_{timestamp}.py"

original = TARGET_FILE.read_text(encoding="utf-8")
backup_file.write_text(original, encoding="utf-8")

old = '''    def _generate_general_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "general_ecommerce_agent_output",
            "content": (
                f"Premium region-aware ecommerce output for {request.region} in {request.language}, "
                f"using {request.currency}. Adapted to local buyer psychology, "
                f"commercial expectations, trust signals, and ecommerce best practices."
            ),
        }'''

new = '''    def _generate_general_output(self, request: GenerationRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "general_ecommerce_agent_output",
            "content": (
                f"Premium region-aware ecommerce output for {request.region} in {request.language}, "
                f"using {request.currency}. Adapted to local buyer psychology, "
                f"commercial expectations, trust signals, and ecommerce best practices."
            ),
            "sections": {
                "premium_expansion_layer": {
                    "general_quality_level": "premium_global_ecommerce_agent_standard",
                    "competitor_benchmark_reference": [
                        "sintra",
                        "manus",
                        "base44",
                        "premium_ecommerce_operator_workflows",
                    ],
                    "execution_focus": [
                        "commercial_usefulness",
                        "region_aware_recommendations",
                        "client_safe_delivery",
                        "clear_next_actions",
                        "risk_awareness",
                        "owner_governed_decisioning",
                        "white_label_saas_readiness",
                    ],
                    "output_requirements": [
                        "provide practical ecommerce actions",
                        "adapt to region language and currency",
                        "avoid generic filler",
                        "separate recommendation from execution",
                        "flag sensitive actions for owner approval",
                        "preserve client-safe wording",
                    ],
                    "localisation": {
                        "region": request.region,
                        "language": request.language,
                        "currency": request.currency,
                        "regional_market_context_applied": True,
                    },
                    "governance": {
                        "client_safe": True,
                        "internal_prompt_exposure_blocked": True,
                        "backend_architecture_exposure_blocked": True,
                        "spending_requires_owner_approval": True,
                        "strategy_change_requires_owner_approval": True,
                        "scaling_requires_owner_approval": True,
                    },
                }
            },
        }'''

if old not in original:
    print("TARGET_BLOCK_NOT_FOUND")
    raise SystemExit(1)

updated = original.replace(old, new, 1)

TARGET_FILE.write_text(updated, encoding="utf-8")

print("STEP_94_GENERAL_AGENT_QUALITY_EXPANSION_INSTALLED")
print(f"Backup created: {backup_file}")
print(f"Updated: {TARGET_FILE}")