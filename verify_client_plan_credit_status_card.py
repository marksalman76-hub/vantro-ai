from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
component = ROOT / "frontend" / "src" / "components" / "ClientPlanCreditStatusCard.tsx"

client_text = client_page.read_text(encoding="utf-8", errors="ignore")
component_text = component.read_text(encoding="utf-8", errors="ignore") if component.exists() else ""

required = [
    "Plan and credits",
    "Current plan",
    "Available credits",
    "Credit status",
    "Upgrade plan",
    "Buy more credits",
    "Manage billing",
    "/api/billing-subscription-status",
    "/api/package-credit-enforcement-status",
    "/client/billing?",
]

proof = {
    "client_plan_credit_status_attempted": True,
    "client_plan_credit_status_passed": True,
    "component_exists": component.exists(),
    "component_imported": "ClientPlanCreditStatusCard" in client_text,
    "component_mounted": "<ClientPlanCreditStatusCard" in client_text,
    "use_client_first_line_client_page": client_text.splitlines()[0].strip() == '"use client";',
    "use_client_first_line_component": component_text.splitlines()[0].strip() == '"use client";' if component_text else False,
    "required_phrases_present": {item: item in component_text for item in required},
    "stripe_live_charge_attempted": False,
    "billing_mutation_attempted": False,
    "credit_mutation_attempted": False,
    "provider_call_attempted": False,
    "media_generation_attempted": False,
    "aws21_or_later_work_attempted": False,
    "public_cutover_enabled": False,
}

proof["client_plan_credit_status_passed"] = (
    proof["component_exists"]
    and proof["component_imported"]
    and proof["component_mounted"]
    and proof["use_client_first_line_client_page"]
    and proof["use_client_first_line_component"]
    and all(proof["required_phrases_present"].values())
)

print("CLIENT_PLAN_CREDIT_STATUS_PROOF:")
print(json.dumps(proof, indent=2, sort_keys=True))

if not proof["client_plan_credit_status_passed"]:
    raise SystemExit("CLIENT_PLAN_CREDIT_STATUS_FAILED")

print("CLIENT_PLAN_CREDIT_STATUS_PASSED")
