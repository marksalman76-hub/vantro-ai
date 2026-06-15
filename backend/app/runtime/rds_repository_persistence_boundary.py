from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional
import uuid

from backend.app.runtime.rds_postgres_schema_readiness_boundary import build_rds_schema_inventory
from backend.app.runtime.real_agent_component_catalogue import (
    CLIENT_FACING_AGENTS,
    FINAL_APPROVED_VISIBLE_AGENT_COUNT,
    FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
    SYSTEM_AGENT_INTERNAL_CAPABILITY_MAPPINGS,
)


REPOSITORY_OPERATION_TYPES = {
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

REPOSITORY_COVERAGE_GROUPS = {
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

OPERATION_TARGETS = {
    "create_job_placeholder": ("jobs", "agent_task_job_records"),
    "update_job_status_placeholder": ("jobs", "agent_task_job_records"),
    "append_job_event_placeholder": ("audit_events", "audit_logs_execution_evidence"),
    "persist_asset_reference_placeholder": ("assets", "assets_uploads_generated_outputs"),
    "persist_queue_message_placeholder": ("queue_messages", "queue_worker_attempts"),
    "persist_worker_attempt_placeholder": ("worker_attempts", "queue_worker_attempts"),
    "persist_provider_attempt_placeholder": ("provider_attempts", "provider_attempts"),
    "persist_billing_ledger_entry_placeholder": ("billing_ledger", "billing_credits_packages"),
    "persist_approval_record_placeholder": ("approvals", "approvals_owner_controls"),
    "persist_audit_event_placeholder": ("audit_events", "audit_logs_execution_evidence"),
    "persist_support_action_placeholder": ("support_actions", "support_admin_recovery"),
    "read_job_status_placeholder": ("jobs", "agent_task_job_records"),
    "list_customer_jobs_placeholder": ("jobs", "agent_task_job_records"),
}

NO_DB_WRITE_MODE = "no_db_write_placeholder"

SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "database_url",
    "password",
    "private_key",
    "provider_api_key",
    "stripe_secret_key",
    "secret",
    "token",
)

SAFE_BOOLEAN_MARKER_KEYS = {
    "credential_values_exposed",
    "provider_secret_values_visible",
    "db_connection_attempted",
    "credentials_required",
    "rds_write_attempted",
    "aws_call_attempted",
    "stripe_call_attempted",
    "provider_call_attempted",
    "credit_mutation_attempted",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "rds_repo_op") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def first_value(payload: Mapping[str, Any], keys: Iterable[str], default: Any = "") -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return default


def ensure_list(value: Any) -> List[str]:
    if isinstance(value, list):
        items = value
    elif isinstance(value, tuple):
        items = list(value)
    elif clean_text(value):
        items = [value]
    else:
        items = []
    result: List[str] = []
    for item in items:
        clean = clean_text(item, 180).lower()
        if clean and clean not in result:
            result.append(clean)
    return result


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if key_l in SAFE_BOOLEAN_MARKER_KEYS:
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


def coerce_record(payload_or_envelope: Mapping[str, Any] | None) -> Dict[str, Any]:
    payload = dict(payload_or_envelope or {})
    if "envelope" in payload and isinstance(payload.get("envelope"), dict):
        return {**dict(payload["envelope"]), **payload}
    return payload


def build_visible_agent_repository_validation(record: Mapping[str, Any]) -> Dict[str, Any]:
    visible_keys = {agent["key"] for agent in CLIENT_FACING_AGENTS}
    internal_source_keys = set(SYSTEM_AGENT_INTERNAL_CAPABILITY_MAPPINGS.keys())
    selected_agents = ensure_list(record.get("selected_agents") or record.get("agent_ids") or record.get("selected_agent"))
    invalid_visible_agent_keys = [
        key for key in selected_agents if key and key not in visible_keys
    ]
    internal_only_agent_keys = [
        key for key in selected_agents if key in internal_source_keys
    ]
    return {
        "source": FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
        "expected_visible_agent_count": FINAL_APPROVED_VISIBLE_AGENT_COUNT,
        "actual_visible_agent_count": len(CLIENT_FACING_AGENTS),
        "selected_agents": selected_agents,
        "invalid_visible_agent_keys": invalid_visible_agent_keys,
        "internal_only_agent_keys": internal_only_agent_keys,
        "visible_agent_reference_valid": not invalid_visible_agent_keys,
        "internal_layers_may_be_referenced_separately": True,
        "system_agents_visible_or_selectable": False,
    }


def operation_target(operation_type: str) -> tuple[str, str]:
    return OPERATION_TARGETS.get(operation_type, ("audit_events", "audit_logs_execution_evidence"))


def audit_from_payload(payload: Mapping[str, Any], operation_type: str) -> Dict[str, Any]:
    nested_audit = payload.get("audit") if isinstance(payload.get("audit"), dict) else {}
    return {
        "correlation_id": clean_text(first_value(payload, ("correlation_id",), nested_audit.get("correlation_id") or safe_id("corr")), 180),
        "request_id": clean_text(first_value(payload, ("request_id",), nested_audit.get("request_id") or ""), 180),
        "idempotency_key": clean_text(first_value(payload, ("idempotency_key",), nested_audit.get("idempotency_key") or ""), 180),
        "audit_event_type": operation_type,
        "source_boundary": "aws13_rds_repository_persistence_boundary",
    }


@dataclass(frozen=True)
class CanonicalRdsRepositoryOperationResult:
    operation_id: str
    operation_type: str
    target_table_or_group: str
    target_table: str = ""
    target_group: str = ""
    job_id: str = ""
    customer_id: str = ""
    account_id: str = ""
    tenant_id: str = ""
    actor_role: str = "system"
    mutation_mode: str = NO_DB_WRITE_MODE
    db_connection_attempted: bool = False
    credentials_required: bool = False
    status: str = "repository_placeholder_planned"
    audit: Dict[str, Any] = field(default_factory=dict)
    visible_agent_validation: Dict[str, Any] = field(default_factory=dict)
    schema_coverage: Dict[str, Any] = field(default_factory=dict)
    record_summary: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    admin_safe_view: Dict[str, Any] = field(default_factory=dict)
    client_safe_view: Dict[str, Any] = field(default_factory=dict)
    rds_write_attempted: bool = False
    migration_executed: bool = False
    aws_call_attempted: bool = False
    stripe_call_attempted: bool = False
    provider_call_attempted: bool = False
    credit_mutation_attempted: bool = False
    credential_values_exposed: bool = False
    provider_secret_values_visible: bool = False
    customer_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_admin_safe_repository_diagnostics(operation: Mapping[str, Any]) -> Dict[str, Any]:
    return redact_secret_values({
        "operation_id": operation.get("operation_id"),
        "operation_type": operation.get("operation_type"),
        "target_table_or_group": operation.get("target_table_or_group"),
        "target_table": operation.get("target_table"),
        "target_group": operation.get("target_group"),
        "job_id": operation.get("job_id"),
        "customer_id": operation.get("customer_id"),
        "account_id": operation.get("account_id"),
        "tenant_id": operation.get("tenant_id"),
        "actor_role": operation.get("actor_role"),
        "mutation_mode": operation.get("mutation_mode"),
        "db_connection_attempted": False,
        "credentials_required": False,
        "status": operation.get("status"),
        "audit": operation.get("audit") or {},
        "visible_agent_validation": operation.get("visible_agent_validation") or {},
        "schema_coverage": operation.get("schema_coverage") or {},
        "record_summary": operation.get("record_summary") or {},
        "rds_write_attempted": False,
        "migration_executed": False,
        "aws_call_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    })


def build_client_safe_repository_status(operation: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "operation_id": operation.get("operation_id"),
        "job_id": operation.get("job_id"),
        "status": operation.get("status"),
        "message": "Durable persistence readiness has been recorded. No database write has been performed.",
        "db_connection_attempted": False,
        "credentials_required": False,
        "rds_write_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "internal_config_exposed": False,
        "customer_safe": True,
    }


def build_repository_operation_result(
    operation_type: str,
    record_or_payload: Mapping[str, Any] | None,
    *,
    target_override: Optional[str] = None,
) -> Dict[str, Any]:
    if operation_type not in REPOSITORY_OPERATION_TYPES:
        operation_type = "persist_audit_event_placeholder"
    record = coerce_record(record_or_payload)
    target_table, target_group = operation_target(operation_type)
    target_table_or_group = clean_text(target_override or target_table or target_group, 180)
    schema_inventory = build_rds_schema_inventory()
    schema_groups = set(schema_inventory.get("schema_groups") or [])
    tables = {table.get("table"): table for table in schema_inventory.get("tables") or []}
    validation = build_visible_agent_repository_validation(record)
    status = "repository_placeholder_planned"
    if validation.get("internal_only_agent_keys") and operation_type in {"create_job_placeholder", "update_job_status_placeholder"}:
        status = "repository_plan_blocked_internal_agent_visible_reference"

    base = {
        "operation_id": clean_text(record.get("operation_id") or safe_id("rds_repo_op"), 180),
        "operation_type": operation_type,
        "target_table_or_group": target_table_or_group,
        "target_table": target_table,
        "target_group": target_group,
        "job_id": clean_text(first_value(record, ("job_id", "parent_job_id"), ""), 180),
        "customer_id": clean_text(first_value(record, ("customer_id", "client_id"), ""), 180),
        "account_id": clean_text(first_value(record, ("account_id", "tenant_id"), ""), 180),
        "tenant_id": clean_text(record.get("tenant_id"), 180),
        "actor_role": clean_text(first_value(record, ("actor_role", "requested_by_role", "role"), "system"), 80),
        "mutation_mode": NO_DB_WRITE_MODE,
        "db_connection_attempted": False,
        "credentials_required": False,
        "status": status,
        "audit": audit_from_payload(record, operation_type),
        "visible_agent_validation": validation,
        "schema_coverage": {
            "target_group_present": target_group in schema_groups,
            "target_table_present": target_table in tables,
            "covered_groups": sorted(REPOSITORY_COVERAGE_GROUPS),
            "schema_inventory_available": True,
        },
        "record_summary": {
            "task_type": clean_text(record.get("task_type"), 120),
            "workflow_type": clean_text(record.get("workflow_type"), 160),
            "asset_type": clean_text(record.get("asset_type"), 120),
            "media_type": clean_text(record.get("media_type"), 120),
            "event_type": clean_text(record.get("event_type"), 120),
            "source_type": clean_text(record.get("source_type"), 120),
            "provider_class": clean_text(record.get("provider_class"), 120),
            "provider_name_present": bool(clean_text(record.get("provider_name") or record.get("provider"))),
        },
        "rds_write_attempted": False,
        "migration_executed": False,
        "aws_call_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    }
    operation = CanonicalRdsRepositoryOperationResult(
        admin_safe_view=build_admin_safe_repository_diagnostics(base),
        client_safe_view=build_client_safe_repository_status(base),
        **base,
    )
    return operation.to_dict()


def build_repository_plan_from_accepted_envelope(envelope: Mapping[str, Any] | None) -> Dict[str, Any]:
    envelope = coerce_record(envelope)
    operations = [
        build_repository_operation_result("create_job_placeholder", envelope),
        build_repository_operation_result("append_job_event_placeholder", envelope),
    ]
    if envelope.get("queue_message"):
        operations.append(build_repository_operation_result("persist_queue_message_placeholder", envelope.get("queue_message") or {}))
    for asset in envelope.get("asset_placeholders") or []:
        if isinstance(asset, dict):
            operations.append(build_repository_operation_result("persist_asset_reference_placeholder", asset))
    if envelope.get("acceptance_enforcement"):
        operations.append(build_repository_operation_result("persist_approval_record_placeholder", envelope.get("acceptance_enforcement") or {}))
    return {
        "plan_type": "accepted_envelope_repository_plan",
        "operations": operations,
        "operation_count": len(operations),
        "db_connection_attempted": False,
        "credentials_required": False,
        "mutation_mode": NO_DB_WRITE_MODE,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_repository_plan_from_billing_ledger_entry(entry: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_repository_operation_result("persist_billing_ledger_entry_placeholder", entry)


def build_repository_plan_from_asset_reference(asset_reference: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_repository_operation_result("persist_asset_reference_placeholder", asset_reference)


def build_repository_plan_from_worker_result(worker_result: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_repository_operation_result("persist_worker_attempt_placeholder", worker_result)


def build_repository_plan_from_queue_message(queue_message: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_repository_operation_result("persist_queue_message_placeholder", queue_message)


def build_repository_plan_from_provider_attempt(provider_attempt: Mapping[str, Any] | None) -> Dict[str, Any]:
    return build_repository_operation_result("persist_provider_attempt_placeholder", provider_attempt)


def validate_repository_operation_result(operation: Mapping[str, Any] | None) -> Dict[str, Any]:
    operation = dict(operation or {})
    errors: List[str] = []
    for key in ("operation_id", "operation_type", "target_table_or_group", "mutation_mode", "status", "audit", "created_at"):
        if key not in operation:
            errors.append(f"missing_{key}")
    if operation.get("operation_type") not in REPOSITORY_OPERATION_TYPES:
        errors.append("unsupported_operation_type")
    if operation.get("mutation_mode") != NO_DB_WRITE_MODE:
        errors.append("mutation_mode_not_placeholder")
    for key in ("db_connection_attempted", "rds_write_attempted", "migration_executed", "aws_call_attempted", "stripe_call_attempted", "provider_call_attempted", "credit_mutation_attempted"):
        if operation.get(key):
            errors.append(key)
    validation = operation.get("visible_agent_validation") or {}
    if validation.get("internal_only_agent_keys") and operation.get("target_group") == "final_approved_visible_agents":
        errors.append("internal_agent_visible_repository_reference")
    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "db_connection_attempted": False,
        "credentials_required": False,
        "rds_write_attempted": False,
        "aws_call_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def build_rds_repository_boundary_readiness() -> Dict[str, Any]:
    schema = build_rds_schema_inventory()
    table_groups = {table["group"] for table in schema.get("tables") or []}
    missing_groups = sorted(group for group in REPOSITORY_COVERAGE_GROUPS if group not in table_groups)
    return {
        "boundary": "aws13_rds_repository_persistence_boundary",
        "repository_operation_types": sorted(REPOSITORY_OPERATION_TYPES),
        "covered_repository_groups": sorted(REPOSITORY_COVERAGE_GROUPS),
        "missing_repository_groups": missing_groups,
        "schema_inventory_available": True,
        "db_connection_attempted": False,
        "credentials_required": False,
        "mutation_mode": NO_DB_WRITE_MODE,
        "rds_write_attempted": False,
        "migration_executed": False,
        "aws_call_attempted": False,
        "stripe_call_attempted": False,
        "provider_call_attempted": False,
        "credit_mutation_attempted": False,
        "final_visible_agent_catalogue": {
            "source": FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
            "expected_count": FINAL_APPROVED_VISIBLE_AGENT_COUNT,
            "actual_count": len(CLIENT_FACING_AGENTS),
            "system_agents_visible_or_selectable": False,
        },
        "credential_values_exposed": False,
        "customer_safe": True,
    }
