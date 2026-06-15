from __future__ import annotations

from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parent


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


def assert_no_db_write(operation: dict) -> None:
    require(operation["mutation_mode"] == "no_db_write_placeholder", "Repository operation must stay no-db-write placeholder.")
    for key in [
        "db_connection_attempted",
        "rds_write_attempted",
        "migration_executed",
        "aws_call_attempted",
        "stripe_call_attempted",
        "provider_call_attempted",
        "credit_mutation_attempted",
    ]:
        require(operation[key] is False, f"Repository boundary must not mutate/call external systems: {key}")


def main() -> int:
    repository = load_module(
        "backend/app/runtime/rds_repository_persistence_boundary.py",
        "rds_repository_persistence_boundary_under_test",
    )
    acceptance = load_module(
        "backend/app/runtime/api_job_acceptance_boundary.py",
        "api_job_acceptance_boundary_for_rds_repo_test",
    )
    billing = load_module(
        "backend/app/runtime/billing_credit_ledger_boundary.py",
        "billing_credit_ledger_boundary_for_rds_repo_test",
    )
    assets = load_module(
        "backend/app/runtime/durable_asset_storage_adapter_boundary.py",
        "durable_asset_storage_adapter_for_rds_repo_test",
    )
    s3 = load_module(
        "backend/app/runtime/s3_asset_delivery_boundary.py",
        "s3_asset_delivery_boundary_for_rds_repo_test",
    )
    queue = load_module(
        "backend/app/runtime/media_queue_adapter_boundary.py",
        "media_queue_adapter_boundary_for_rds_repo_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_rds_repo_test",
    )

    source = read("backend/app/runtime/rds_repository_persistence_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in [
        "psycopg",
        "sqlite3",
        "connect(",
        "cursor(",
        "execute(",
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
        "CREATE TABLE",
        "boto3",
        "requests.",
        "httpx.",
        "stripe.",
    ]:
        require(marker not in source, f"AWS-13 repository boundary must not contain live DB/AWS/network marker: {marker}")

    readiness = repository.build_rds_repository_boundary_readiness()
    expected_operation_types = {
        "create_job_placeholder",
        "update_job_status_placeholder",
        "append_job_event_placeholder",
        "persist_asset_reference_placeholder",
        "persist_queue_message_placeholder",
        "persist_worker_attempt_placeholder",
        "persist_provider_attempt_placeholder",
        "persist_billing_ledger_entry_placeholder",
        "persist_approval_record_placeholder",
        "persist_audit_event_placeholder",
        "persist_support_action_placeholder",
        "read_job_status_placeholder",
        "list_customer_jobs_placeholder",
    }
    require(expected_operation_types == set(readiness["repository_operation_types"]), "AWS-13 must expose all canonical repository operation types.")
    expected_groups = {
        "accounts_customers",
        "users_session_references",
        "final_approved_visible_agents",
        "internal_capabilities_runtime_layers",
        "agent_task_job_records",
        "media_job_details",
        "assets_uploads_generated_outputs",
        "queue_worker_attempts",
        "provider_attempts",
        "billing_credits_packages",
        "stripe_event_references",
        "approvals_owner_controls",
        "audit_logs_execution_evidence",
        "support_admin_recovery",
        "integrations",
        "learning_memory_governance",
        "observability_correlation",
    }
    require(expected_groups.issubset(set(readiness["covered_repository_groups"])), "AWS-13 must cover the full SaaS repository surface.")
    require(readiness["missing_repository_groups"] == [], f"Repository readiness missing groups: {readiness['missing_repository_groups']}")
    require(readiness["db_connection_attempted"] is False, "Readiness must not connect to DB.")
    require(readiness["credentials_required"] is False, "Readiness must not require credentials.")
    require(readiness["mutation_mode"] == "no_db_write_placeholder", "Readiness mutation mode must be no-db-write.")

    accepted_envelope = acceptance.build_api_job_acceptance_envelope({
        "job_id": "job_rds_repo_aws13",
        "customer_id": "client_123",
        "account_id": "account_123",
        "actor_role": "client",
        "package_name": "business",
        "entitlement_status": "active",
        "task_type": "media_generation",
        "workflow_type": "universal_complete_media",
        "selected_agent": "marketing_specialist_agent",
        "selected_agents": ["marketing_specialist_agent", "ugc_media_agent"],
        "agent_ids": ["marketing_specialist_agent", "ugc_media_agent"],
        "active_agents": ["marketing_specialist_agent", "ugc_media_agent"],
        "media_type": "complete_video",
        "asset_type": "final_mp4",
        "duration_seconds": 10,
        "video_provider": "future_video_provider",
        "credit_reservation_status": "reserved",
        "approval_status": "owner_approved",
        "correlation_id": "corr_rds_repo_aws13",
        "database_url": "postgres://SHOULD_NOT_LEAK",
        "stripe_secret_key": "STRIPE_SECRET_SHOULD_NOT_LEAK",
    })
    envelope_plan = repository.build_repository_plan_from_accepted_envelope(accepted_envelope)
    require(envelope_plan["plan_type"] == "accepted_envelope_repository_plan", "Repository must build plan from AWS-05 accepted envelope.")
    require(envelope_plan["operation_count"] >= 4, "Accepted envelope plan should include job, event, queue, asset, and approval placeholders.")
    require(envelope_plan["db_connection_attempted"] is False, "Accepted envelope plan must not connect to DB.")
    for operation in envelope_plan["operations"]:
        assert_no_db_write(operation)
        validation = repository.validate_repository_operation_result(operation)
        require(validation["valid"] is True, f"Repository operation should validate: {validation}")
    require("postgres://SHOULD_NOT_LEAK" not in str(envelope_plan), "Repository plan must redact database URL values.")
    require("STRIPE_SECRET_SHOULD_NOT_LEAK" not in str(envelope_plan), "Repository plan must redact Stripe secret values.")

    billing_entry = billing.build_credit_reservation_placeholder(accepted_envelope)
    billing_op = repository.build_repository_plan_from_billing_ledger_entry(billing_entry)
    require(billing_op["operation_type"] == "persist_billing_ledger_entry_placeholder", "Repository must consume AWS-12 billing ledger entry.")
    require(billing_op["target_table"] == "billing_ledger", "Billing entry should target billing ledger table placeholder.")
    assert_no_db_write(billing_op)

    asset_ref = assets.build_asset_reference_from_local_path(
        "runtime_outputs/job_rds_repo_aws13/final.mp4",
        "final_video",
        asset_id="asset_rds_repo_aws13",
        job_id="job_rds_repo_aws13",
        customer_id="client_123",
        source_type="composed_output",
        source_metadata={"provider_api_key": "PROVIDER_SECRET_SHOULD_NOT_LEAK"},
    )
    asset_op = repository.build_repository_plan_from_asset_reference(asset_ref)
    require(asset_op["operation_type"] == "persist_asset_reference_placeholder", "Repository must consume durable asset reference.")
    require(asset_op["target_table"] == "assets", "Asset reference should target assets table placeholder.")
    assert_no_db_write(asset_op)
    require("PROVIDER_SECRET_SHOULD_NOT_LEAK" not in str(asset_op), "Repository asset operation must redact provider secrets.")

    s3_ref = s3.build_s3_object_reference_from_asset_reference(asset_ref, env={"AWS_MEDIA_S3_BUCKET": "future-media-bucket"})
    s3_op = repository.build_repository_plan_from_asset_reference(s3_ref)
    require(s3_op["target_table"] == "assets", "Repository must consume future S3 reference as asset placeholder.")
    assert_no_db_write(s3_op)

    queue_message = queue.build_media_queue_message({
        "job_id": "job_rds_repo_queue",
        "customer_id": "client_123",
        "selected_agent": "marketing_specialist_agent",
        "selected_agents": ["marketing_specialist_agent"],
        "video_provider": "future_video_provider",
    })
    queue_op = repository.build_repository_plan_from_queue_message(queue_message)
    require(queue_op["operation_type"] == "persist_queue_message_placeholder", "Repository must consume queue message.")
    require(queue_op["target_table"] == "queue_messages", "Queue message should target queue_messages placeholder.")
    assert_no_db_write(queue_op)

    worker_op = repository.build_repository_plan_from_worker_result({
        "job_id": "job_rds_repo_worker",
        "attempt_id": "attempt_123",
        "worker_type": "ecs_media_worker",
        "status": "running",
        "correlation_id": "corr_worker",
    })
    provider_op = repository.build_repository_plan_from_provider_attempt({
        "job_id": "job_rds_repo_provider",
        "provider": "future_video_provider",
        "provider_class": "video_generation_providers",
        "provider_job_id": "provider_job_123",
        "safe_error_summary": "",
    })
    require(worker_op["target_table"] == "worker_attempts", "Worker result should target worker_attempts placeholder.")
    require(provider_op["target_table"] == "provider_attempts", "Provider attempt should target provider_attempts placeholder.")
    assert_no_db_write(worker_op)
    assert_no_db_write(provider_op)

    operation_targets = {
        "persist_approval_record_placeholder": "approvals",
        "persist_audit_event_placeholder": "audit_events",
        "persist_support_action_placeholder": "support_actions",
        "read_job_status_placeholder": "jobs",
        "list_customer_jobs_placeholder": "jobs",
    }
    for operation_type, table in operation_targets.items():
        op = repository.build_repository_operation_result(operation_type, {
            "job_id": f"job_{operation_type}",
            "customer_id": "client_123",
            "actor_role": "admin",
            "correlation_id": f"corr_{operation_type}",
        })
        require(op["target_table"] == table, f"{operation_type} should target {table}.")
        assert_no_db_write(op)

    internal_agent_op = repository.build_repository_operation_result("create_job_placeholder", {
        "job_id": "job_internal_agent_block",
        "selected_agent": "orchestration_agent",
        "selected_agents": ["orchestration_agent"],
        "actor_role": "client",
    })
    require(internal_agent_op["status"] == "repository_plan_blocked_internal_agent_visible_reference", "Repository must block internal agent as visible job reference.")
    require(internal_agent_op["visible_agent_validation"]["internal_only_agent_keys"] == ["orchestration_agent"], "Internal agent diagnostics missing.")
    assert_no_db_write(internal_agent_op)

    admin_view = repository.build_admin_safe_repository_diagnostics(billing_op)
    client_view = repository.build_client_safe_repository_status(billing_op)
    require("target_table" in admin_view, "Admin repository diagnostics should include target table.")
    require("schema_coverage" in admin_view, "Admin repository diagnostics should include schema coverage.")
    require("target_table" not in client_view, "Client repository view must hide table/internal details.")
    require("schema_coverage" not in client_view, "Client repository view must hide schema details.")
    require(client_view["db_connection_attempted"] is False, "Client view must show no DB connection.")
    require(client_view["credentials_required"] is False, "Client view must show no credentials required.")

    visible = catalogue.list_final_approved_visible_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(visible["count"] == 27, "AWS-13 must not alter final 27 visible catalogue count.")
    require(enterprise_selectable["count"] == 27, "AWS-13 must not alter enterprise selectable count.")
    require(not system_keys.intersection(selectable_keys), "AWS-13 must not expose SYSTEM_AGENTS as client-selectable.")

    for marker in [
        "CanonicalRdsRepositoryOperationResult",
        "REPOSITORY_OPERATION_TYPES",
        "build_repository_plan_from_accepted_envelope",
        "build_repository_plan_from_billing_ledger_entry",
        "build_repository_plan_from_asset_reference",
        "build_repository_plan_from_worker_result",
        "build_repository_plan_from_queue_message",
        "validate_repository_operation_result",
        "no_db_write_placeholder",
    ]:
        require(marker in source, f"AWS-13 source missing marker: {marker}")

    for marker in [
        "AWS-13",
        "RDS repository persistence boundary",
        "verify_rds_repository_persistence_boundary.py",
        "no database connection, migration, credential requirement, or write",
        "full SaaS repository interface",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-13 marker: {marker}")

    print("RDS_REPOSITORY_PERSISTENCE_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
