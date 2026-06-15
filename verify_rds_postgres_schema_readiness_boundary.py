from __future__ import annotations

from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parent


REQUIRED_SCHEMA_GROUPS = {
    "accounts_customers",
    "users_session_references",
    "final_approved_visible_agents",
    "internal_capabilities_runtime_layers",
    "agent_task_job_records",
    "media_job_details",
    "queue_worker_attempts",
    "assets_uploads_generated_outputs",
    "billing_credits_packages",
    "stripe_event_references",
    "approvals_owner_controls",
    "provider_attempts",
    "audit_logs_execution_evidence",
    "support_admin_recovery",
    "integrations",
    "learning_memory_governance",
    "observability_correlation",
    "admin_client_visibility_rules",
}

SYSTEM_CAPABILITY_KEYS = {
    "orchestration_agent",
    "security_compliance_agent",
    "qa_testing_agent",
    "integration_automation_agent",
    "billing_optimisation_agent",
    "training_learning_agent",
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8", errors="ignore")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AssertionError(f"Could not load module: {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    rds = load_module(
        "backend/app/runtime/rds_postgres_schema_readiness_boundary.py",
        "rds_postgres_schema_readiness_boundary_under_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_rds_test",
    )
    aws_contract = load_module(
        "backend/app/runtime/aws_option_a_runtime_contract.py",
        "aws_option_a_runtime_contract_for_rds_test",
    )
    source = read("backend/app/runtime/rds_postgres_schema_readiness_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    readiness = rds.build_rds_postgres_schema_readiness({})
    admin_view = rds.admin_rds_schema_readiness_view(readiness)
    client_view = rds.client_rds_schema_readiness_view(readiness)
    local_contract = aws_contract.aws_option_a_readiness({})
    inventory = readiness["schema_inventory"]
    table_groups = {table["group"] for table in inventory["tables"]}
    table_names = {table["table"] for table in inventory["tables"]}

    require(readiness["database_mode_enabled"] is False, "RDS schema readiness must keep database mode disabled by default.")
    require(readiness["database_connection_attempted"] is False, "RDS schema readiness must not connect to a database.")
    require(readiness["migrations_executed"] is False, "RDS schema readiness must not run migrations.")
    require(readiness["credentials_required_now"] is False, "RDS schema readiness must not require credentials now.")
    require(readiness["credential_values_exposed"] is False, "RDS schema readiness must not expose credentials.")
    require(readiness["secret_values_visible"] is False, "RDS schema readiness must not expose secret values.")
    require(readiness["rds_calls_started"] is False, "RDS calls must not start.")
    require(readiness["aws_calls_started"] is False, "AWS calls must not start.")
    require(readiness["stripe_calls_started"] is False, "Stripe calls must not start.")
    require(readiness["provider_calls_started"] is False, "Provider calls must not start.")
    require(readiness["billing_credit_mutation_started"] is False, "Billing/credit mutation must not start.")
    require(local_contract["aws_option_a_enabled"] is False, "AWS Option A must remain disabled by default.")
    require(local_contract["ready_for_aws_execution"] is False, "Local/default mode must not require RDS readiness.")

    require(set(readiness["schema_inventory"]["schema_groups"]) == REQUIRED_SCHEMA_GROUPS, "Schema group inventory must match full SaaS required groups.")
    require(REQUIRED_SCHEMA_GROUPS <= table_groups, "Every required schema group must have at least one table spec.")
    require(readiness["table_coverage_complete"] is True, "Full SaaS table coverage must be complete.")
    require(readiness["missing_schema_groups"] == [], "No required schema group should be missing.")

    for expected_table in [
        "accounts",
        "users",
        "sessions",
        "visible_agents",
        "internal_capabilities",
        "agent_tasks",
        "jobs",
        "media_jobs",
        "queue_messages",
        "worker_attempts",
        "assets",
        "billing_ledger",
        "packages",
        "stripe_events",
        "approvals",
        "provider_attempts",
        "audit_events",
        "execution_evidence",
        "support_actions",
        "integrations",
        "learning_memory_records",
        "observability_events",
        "visibility_policies",
    ]:
        require(expected_table in table_names, f"Schema inventory missing table: {expected_table}")

    visible_catalogue = readiness["final_visible_agent_catalogue"]
    visible_rows = inventory["visible_agent_rows"]
    visible_keys = {row["agent_key"] for row in visible_rows}
    client_keys = {agent["key"] for agent in catalogue.CLIENT_FACING_AGENTS}
    require(visible_catalogue["source"] == "CLIENT_FACING_AGENTS", "Visible agent source must be CLIENT_FACING_AGENTS.")
    require(visible_catalogue["expected_count"] == 27, "Visible agent expected count must be 27.")
    require(visible_catalogue["actual_count"] == 27, "Visible agent actual count must be 27.")
    require(visible_catalogue["only_client_facing_agents"] is True, "Visible agents must come only from CLIENT_FACING_AGENTS.")
    require(visible_catalogue["system_agents_visible_or_selectable"] is False, "System agents must not be visible/selectable.")
    require(visible_keys == client_keys, "Visible agent rows must exactly match CLIENT_FACING_AGENTS.")
    require(not (visible_keys & SYSTEM_CAPABILITY_KEYS), "Visible agent rows must not include folded system agents.")
    require(all(row["visible_catalogue_agent"] is True for row in visible_rows), "Visible rows must be visible catalogue agents.")

    internal_catalogue = readiness["internal_capability_catalogue"]
    internal_rows = inventory["internal_capability_rows"]
    internal_keys = {row["source_system_agent_key"] for row in internal_rows}
    require(internal_catalogue["source"] == "SYSTEM_AGENT_INTERNAL_CAPABILITY_MAPPINGS", "Internal capability source mismatch.")
    require(internal_catalogue["count"] == 6, "Internal capability count must be six folded system capabilities.")
    require(internal_catalogue["all_internal_only"] is True, "All folded system capabilities must be internal-only.")
    require(internal_keys == SYSTEM_CAPABILITY_KEYS, "Internal capability rows must model the six folded system agents.")
    require(all(row["visible_catalogue_agent"] is False for row in internal_rows), "Internal capabilities must not be visible agents.")
    require(all(row["client_selectable"] is False for row in internal_rows), "Internal capabilities must not be client selectable.")
    for row in internal_rows:
        require(row["approved_owner_agent"] in client_keys, f"Internal capability owner must be an approved visible agent: {row}")

    for domain_marker in [
        "billing_credits_packages",
        "stripe_event_references",
        "approvals_owner_controls",
        "audit_logs_execution_evidence",
        "support_admin_recovery",
        "integrations",
        "learning_memory_governance",
        "observability_correlation",
        "admin_client_visibility_rules",
    ]:
        require(domain_marker in str(inventory), f"Schema readiness missing full-SaaS domain marker: {domain_marker}")

    require("schema_inventory" in admin_view, "Admin view must include schema inventory.")
    require("schema_inventory" not in client_view, "Client view must hide schema inventory internals.")
    require(client_view["status"] == "database_schema_planned", "Client view must expose friendly planned status.")
    require(client_view["credential_values_exposed"] is False, "Client view must not expose credentials.")
    require("DATABASE_URL_VALUE" not in str(admin_view), "Admin view must not expose database secret values.")

    for forbidden in [
        "psycopg",
        "asyncpg",
        "create_engine",
        "connect(",
        "subprocess",
        "boto3",
        "stripe.",
        "requests.",
        "httpx.",
    ]:
        require(forbidden not in source, f"RDS readiness boundary must not introduce live side-effect dependency: {forbidden}")

    for marker in [
        "RdsPostgresSchemaReadiness",
        "build_rds_schema_inventory",
        "build_rds_postgres_schema_readiness",
        "admin_rds_schema_readiness_view",
        "client_rds_schema_readiness_view",
        "FULL_SAAS_SCHEMA_GROUPS",
        "visible_agent_table_rows",
        "internal_capability_rows",
    ]:
        require(marker in source, f"RDS readiness source missing marker: {marker}")

    for marker in [
        "AWS-08",
        "RDS PostgreSQL schema/readiness boundary",
        "verify_rds_postgres_schema_readiness_boundary.py",
        "final 27 visible agents",
        "internal capabilities/runtime layers",
        "no database migration or connection",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-08 marker: {marker}")

    print("RDS_POSTGRES_SCHEMA_READINESS_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
