from pathlib import Path

checks = {
    "frontend/src/lib/agentCatalogueProductionUx.ts": [
        "AGENT_CATALOGUE",
        "PACKAGE_RULES",
        "getCatalogueForPackage",
        "validateCatalogueSelection",
        "agent_catalogue_production_ux_enabled",
        "selected_locked_after_activation",
        "post_activation_changes_require_owner_approval",
        "head_agent",
        "orchestration_agent",
        "internal_only",
    ],
    "frontend/src/app/api/agent-catalogue-production-ux/route.ts": [
        "getCatalogueForPackage",
        "validateCatalogueSelection",
        "catalogue_total_count",
    ],
    "frontend/src/app/api/signup-agent-selection/options/[plan]/route.ts": [
        "getCatalogueForPackage",
        "cache-control",
    ],
    "frontend/src/app/api/signup-agent-selection/validate/route.ts": [
        "validateCatalogueSelection",
        "selected_agents",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW11_AGENT_CATALOGUE_PRODUCTION_UX_FAILED missing={missing}")

print("ROW11_AGENT_CATALOGUE_PRODUCTION_UX_PASSED")
