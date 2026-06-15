from __future__ import annotations

from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parent


SYSTEM_AGENT_OWNER_MAP = {
    "orchestration_agent": ("head_agent", "hidden_orchestration_runtime_planner"),
    "security_compliance_agent": ("head_agent", "hidden_security_governance_layer"),
    "qa_testing_agent": ("operations_agent", "hidden_quality_runtime_verification_layer"),
    "integration_automation_agent": ("workflow_automation_agent", "hidden_integration_runtime_layer"),
    "billing_optimisation_agent": ("finance_admin_agent", "hidden_billing_credit_package_enforcement_layer"),
    "training_learning_agent": ("customer_success_agent", "hidden_learning_memory_governance_layer"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_catalogue_module():
    path = ROOT / "backend/app/runtime/real_agent_component_catalogue.py"
    spec = importlib.util.spec_from_file_location("real_agent_component_catalogue_under_test", path)
    if not spec or not spec.loader:
        raise AssertionError("Could not load real agent component catalogue module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    catalogue = load_catalogue_module()

    client_agents = list(catalogue.CLIENT_FACING_AGENTS)
    system_agents = list(catalogue.SYSTEM_AGENTS)
    client_keys = [agent["key"] for agent in client_agents]
    system_keys = [agent["key"] for agent in system_agents]
    client_key_set = set(client_keys)
    system_key_set = set(system_keys)

    require(catalogue.FINAL_APPROVED_VISIBLE_AGENT_COUNT == 27, "Final approved visible count constant must be 27.")
    require(catalogue.FINAL_APPROVED_VISIBLE_AGENT_SOURCE == "CLIENT_FACING_AGENTS", "Visible source must be CLIENT_FACING_AGENTS.")
    require(len(client_agents) == 27, "CLIENT_FACING_AGENTS must contain exactly 27 agents.")
    require(len(client_keys) == len(client_key_set), "Visible client-facing agent keys must not contain duplicates.")
    require(not (client_key_set & system_key_set), "SYSTEM_AGENTS must not duplicate visible agent keys.")
    require(set(SYSTEM_AGENT_OWNER_MAP) == system_key_set, "SYSTEM_AGENTS must be exactly the six internal capability keys.")

    visible = catalogue.list_final_approved_visible_agents()
    require(visible["source"] == "CLIENT_FACING_AGENTS", "Final visible helper must use CLIENT_FACING_AGENTS.")
    require(visible["count"] == 27, "Final visible helper must report 27 agents.")
    require(visible["system_agents_visible"] is False, "Final visible helper must exclude system agents.")

    full = catalogue.list_real_agent_component_catalogue()
    counts = catalogue.calculate_catalogue_counts()
    status = catalogue.real_agent_component_catalogue_status()
    require(full["total_visible_agent_count"] == 27, "Total visible agent count must exclude SYSTEM_AGENTS.")
    require(full["final_approved_visible_agent_count"] == 27, "Full catalogue must expose final approved visible count.")
    require(full["system_agents_internal_only"] is True, "Full catalogue must mark system agents internal-only.")
    require(status["visible_agent_count"] == 27, "Status visible agent count must exclude SYSTEM_AGENTS.")
    require(status["system_agents_internal_only"] is True, "Status must mark system agents internal-only.")
    require(counts["final_approved_visible_agents"] == 27, "Counts must report final approved visible agents.")
    require(counts["system_agents_visible_catalogue_agents"] == 0, "No system agent may count as visible catalogue agent.")
    require(counts["system_agents_client_selectable"] == 0, "No system agent may be client selectable.")
    require(
        full["total_operational_component_count"] >= 27 + len(system_agents),
        "Operational component count may include internal system capabilities separately.",
    )

    for plan in ["starter", "business", "enterprise"]:
        selectable = catalogue.list_client_selectable_agents(plan)
        selectable_keys = {agent["key"] for agent in selectable["agents"]}
        require(selectable_keys <= client_key_set, f"{plan} selectable agents must only come from CLIENT_FACING_AGENTS.")
        require(not (selectable_keys & system_key_set), f"{plan} selectable agents must not include SYSTEM_AGENTS.")
        require(selectable["system_agents_client_selectable"] is False, f"{plan} must flag system agents non-selectable.")
        require(selectable["visible_catalogue_source"] == "CLIENT_FACING_AGENTS", f"{plan} must report visible source.")

    mappings = catalogue.SYSTEM_AGENT_INTERNAL_CAPABILITY_MAPPINGS
    require(set(mappings) == system_key_set, "Every system agent must have an internal capability mapping.")
    for system_key, (owner_key, internal_layer) in SYSTEM_AGENT_OWNER_MAP.items():
        system_component = catalogue.get_catalogue_component_by_key(system_key)
        require(system_component["found"] is True, f"System component missing: {system_key}")
        require(system_component["component_type"] == "system_agent", f"{system_key} must remain typed as system_agent.")
        component = system_component["component"]
        require(component["internal_only"] is True, f"{system_key} must be internal_only.")
        require(component["client_selectable"] is False, f"{system_key} must not be client selectable.")
        require(component["visible_catalogue_agent"] is False, f"{system_key} must not be visible catalogue agent.")
        require(component["approved_owner_agent"] == owner_key, f"{system_key} owner mapping is wrong.")
        require(component["internal_layer"] == internal_layer, f"{system_key} internal layer mapping is wrong.")
        require(owner_key in client_key_set, f"{system_key} owner must be an approved visible agent.")
        require(mappings[system_key]["approved_owner_agent"] == owner_key, f"{system_key} mapping owner mismatch.")
        require(mappings[system_key]["internal_layer"] == internal_layer, f"{system_key} mapping layer mismatch.")

    print("FINAL_27_AGENT_CATALOGUE_VISIBILITY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
