from pathlib import Path

checks = {
    "frontend/src/lib/allAgentOutputContracts.ts": [
        "ALL_AGENT_OUTPUT_CONTRACTS",
        "getAgentOutputContract",
        "validateAgentOutputContract",
        "attachAgentOutputContract",
        "all_agent_output_contracts_enabled",
        "quality_passed",
        "client_safe",
        "marketing_specialist_agent",
        "ugc_creative_agent",
        "security_compliance_agent",
    ],
    "frontend/src/app/api/all-agent-output-contracts/route.ts": [
        "ALL_AGENT_OUTPUT_CONTRACTS",
        "validateAgentOutputContract",
        "attachAgentOutputContract",
        "contract_count",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "attachAgentOutputContract",
        "allAgentOutputContracts",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "attachAgentOutputContract",
        "allAgentOutputContracts",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW10_ALL_AGENT_OUTPUT_CONTRACTS_FAILED missing={missing}")

print("ROW10_ALL_AGENT_OUTPUT_CONTRACTS_PASSED")
