from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from backend.app.runtime.aws_option_a_runtime_contract import aws_option_a_readiness
from backend.app.runtime.real_agent_component_catalogue import (
    CLIENT_FACING_AGENTS,
    FINAL_APPROVED_VISIBLE_AGENT_COUNT,
    FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
    SYSTEM_AGENTS,
    SYSTEM_AGENT_INTERNAL_CAPABILITY_MAPPINGS,
)


FULL_SAAS_SCHEMA_GROUPS = [
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
]


def table_spec(name: str, group: str, purpose: str, columns: List[str]) -> Dict[str, Any]:
    return {
        "table": name,
        "group": group,
        "purpose": purpose,
        "columns": columns,
        "postgres_target": True,
        "migration_executed": False,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def visible_agent_table_rows() -> List[Dict[str, Any]]:
    return [
        {
            "agent_key": agent["key"],
            "name": agent["name"],
            "category": agent["category"],
            "enterprise_only": bool(agent.get("enterprise_only")),
            "visible_catalogue_agent": True,
            "client_selectable_source": FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
        }
        for agent in CLIENT_FACING_AGENTS
    ]


def internal_capability_rows() -> List[Dict[str, Any]]:
    rows = []
    system_by_key = {agent["key"]: agent for agent in SYSTEM_AGENTS}
    for key, mapping in SYSTEM_AGENT_INTERNAL_CAPABILITY_MAPPINGS.items():
        system_agent = dict(system_by_key.get(key) or {})
        rows.append({
            "source_system_agent_key": key,
            "source_system_agent_name": system_agent.get("name") or "",
            "approved_owner_agent": mapping["approved_owner_agent"],
            "capability_name": mapping["capability_name"],
            "internal_layer": mapping["internal_layer"],
            "internal_only": True,
            "visible_catalogue_agent": False,
            "client_selectable": False,
        })
    return rows


def build_rds_schema_inventory() -> Dict[str, Any]:
    visible_agents = visible_agent_table_rows()
    internal_capabilities = internal_capability_rows()
    tables = [
        table_spec(
            "accounts",
            "accounts_customers",
            "Tenant/account ownership, package context, and customer isolation root.",
            ["account_id", "customer_id", "account_status", "package_key", "created_at", "updated_at"],
        ),
        table_spec(
            "users",
            "users_session_references",
            "User identity references for admin/client access without storing raw session secrets.",
            ["user_id", "account_id", "role", "email_hash", "auth_provider_ref", "created_at", "updated_at"],
        ),
        table_spec(
            "sessions",
            "users_session_references",
            "Session reference/audit metadata; no raw tokens.",
            ["session_id", "user_id", "account_id", "expires_at", "revoked_at", "created_at"],
        ),
        table_spec(
            "visible_agents",
            "final_approved_visible_agents",
            "Exactly 27 approved visible/selectable agent catalogue records.",
            ["agent_key", "name", "category", "enterprise_only", "visible_catalogue_agent", "client_selectable_source"],
        ),
        table_spec(
            "internal_capabilities",
            "internal_capabilities_runtime_layers",
            "Internal-only capabilities and folded system layers mapped into approved visible agents.",
            ["capability_name", "source_system_agent_key", "approved_owner_agent", "internal_layer", "internal_only", "client_selectable"],
        ),
        table_spec(
            "agent_tasks",
            "agent_task_job_records",
            "Approved-agent task records across media and non-media execution.",
            ["task_id", "account_id", "agent_key", "task_type", "workflow_type", "status", "correlation_id", "created_at", "updated_at"],
        ),
        table_spec(
            "jobs",
            "agent_task_job_records",
            "Durable job lifecycle state for accepted SaaS work.",
            ["job_id", "task_id", "account_id", "client_safe_status", "internal_status", "requested_from", "created_at", "updated_at"],
        ),
        table_spec(
            "media_jobs",
            "media_job_details",
            "Complete media job details, duration, segment plan, provider preferences, and composition state.",
            ["job_id", "media_type", "asset_type", "duration_seconds", "aspect_ratio", "segment_count", "script_packet_ref", "created_at"],
        ),
        table_spec(
            "queue_messages",
            "queue_worker_attempts",
            "Queue/SQS message records and DLQ-aware routing metadata.",
            ["message_id", "job_id", "queue_name", "workflow_type", "attempt_count", "max_attempts", "dlq_target", "created_at"],
        ),
        table_spec(
            "worker_attempts",
            "queue_worker_attempts",
            "Worker lifecycle attempts and safe failure status.",
            ["attempt_id", "job_id", "message_id", "worker_type", "lifecycle_state", "safe_error_summary", "created_at"],
        ),
        table_spec(
            "assets",
            "assets_uploads_generated_outputs",
            "Durable asset references for uploads, generated media, sites, documents, evidence, support files, previews, captions, transcripts, and audio.",
            ["asset_id", "account_id", "job_id", "asset_type", "source_type", "s3_bucket", "s3_key", "client_visible", "admin_visible", "created_at"],
        ),
        table_spec(
            "billing_ledger",
            "billing_credits_packages",
            "Billing and credit ledger references without mutating payment state in this boundary.",
            ["ledger_id", "account_id", "job_id", "package_key", "credit_delta", "reservation_status", "created_at"],
        ),
        table_spec(
            "packages",
            "billing_credits_packages",
            "Package entitlement and feature references.",
            ["package_key", "feature_key", "limit_type", "limit_value", "active"],
        ),
        table_spec(
            "stripe_events",
            "stripe_event_references",
            "Stripe event idempotency and audit references; no Stripe API calls in readiness boundary.",
            ["stripe_event_id", "account_id", "event_type", "processed_status", "created_at"],
        ),
        table_spec(
            "approvals",
            "approvals_owner_controls",
            "Owner/admin approval gates for governed spend and actions.",
            ["approval_id", "account_id", "job_id", "requested_by", "approval_status", "owner_control_status", "created_at"],
        ),
        table_spec(
            "provider_attempts",
            "provider_attempts",
            "Provider attempt metadata and diagnostics without storing credentials.",
            ["attempt_id", "job_id", "provider", "provider_job_id", "status", "safe_error_summary", "created_at"],
        ),
        table_spec(
            "audit_events",
            "audit_logs_execution_evidence",
            "Audit logs, execution evidence, visibility decisions, and correlation trail.",
            ["audit_event_id", "account_id", "job_id", "actor_role", "event_type", "correlation_id", "created_at"],
        ),
        table_spec(
            "execution_evidence",
            "audit_logs_execution_evidence",
            "Evidence records and asset references for admin/client-safe proof of work.",
            ["evidence_id", "job_id", "asset_id", "visibility", "summary", "created_at"],
        ),
        table_spec(
            "support_actions",
            "support_admin_recovery",
            "Admin/support recovery, retry, requeue, cancel, and incident action references.",
            ["support_action_id", "account_id", "job_id", "action_type", "actor_id", "safe_summary", "created_at"],
        ),
        table_spec(
            "integrations",
            "integrations",
            "Connected integration references and health state without raw credentials.",
            ["integration_id", "account_id", "provider", "connection_status", "last_health_check_at", "created_at"],
        ),
        table_spec(
            "learning_memory_records",
            "learning_memory_governance",
            "Governed learning, memory, feedback, and training references.",
            ["memory_id", "account_id", "owner_agent_key", "memory_type", "governance_status", "created_at"],
        ),
        table_spec(
            "observability_events",
            "observability_correlation",
            "Operational metrics, incidents, traces, and correlation IDs for CloudWatch/admin diagnostics.",
            ["event_id", "job_id", "correlation_id", "service_name", "severity", "metric_key", "created_at"],
        ),
        table_spec(
            "visibility_policies",
            "admin_client_visibility_rules",
            "Admin/client visibility rules for records, assets, diagnostics, and evidence.",
            ["policy_id", "record_type", "client_visible", "admin_visible", "redaction_rule", "created_at"],
        ),
    ]
    return {
        "schema_groups": FULL_SAAS_SCHEMA_GROUPS,
        "tables": tables,
        "visible_agent_rows": visible_agents,
        "internal_capability_rows": internal_capabilities,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


@dataclass(frozen=True)
class RdsPostgresSchemaReadiness:
    database_mode_enabled: bool = False
    database_connection_attempted: bool = False
    migrations_executed: bool = False
    credentials_required_now: bool = False
    credential_values_exposed: bool = False
    secret_values_visible: bool = False
    required_env_placeholders: List[str] = field(default_factory=list)
    future_migration_state: Dict[str, Any] = field(default_factory=dict)
    schema_inventory: Dict[str, Any] = field(default_factory=dict)
    table_coverage_complete: bool = False
    final_visible_agent_catalogue: Dict[str, Any] = field(default_factory=dict)
    internal_capability_catalogue: Dict[str, Any] = field(default_factory=dict)
    runtime_readiness: Dict[str, Any] = field(default_factory=dict)
    customer_safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_rds_postgres_schema_readiness(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    readiness = aws_option_a_readiness(env or {})
    schema_inventory = build_rds_schema_inventory()
    covered_groups = {table["group"] for table in schema_inventory["tables"]}
    missing_groups = [group for group in FULL_SAAS_SCHEMA_GROUPS if group not in covered_groups]
    visible_agent_rows = schema_inventory["visible_agent_rows"]
    internal_capability_rows = schema_inventory["internal_capability_rows"]

    result = RdsPostgresSchemaReadiness(
        database_mode_enabled=False,
        database_connection_attempted=False,
        migrations_executed=False,
        credentials_required_now=False,
        credential_values_exposed=False,
        secret_values_visible=False,
        required_env_placeholders=["DATABASE_URL", "AWS_RDS_SECRET_ARN"],
        future_migration_state={
            "migration_tool_selected": False,
            "migration_files_created": False,
            "dry_run_required_before_cutover": True,
            "rollback_plan_required": True,
            "rds_adapter_wiring_required": True,
        },
        schema_inventory=schema_inventory,
        table_coverage_complete=not missing_groups,
        final_visible_agent_catalogue={
            "source": FINAL_APPROVED_VISIBLE_AGENT_SOURCE,
            "expected_count": FINAL_APPROVED_VISIBLE_AGENT_COUNT,
            "actual_count": len(visible_agent_rows),
            "only_client_facing_agents": True,
            "system_agents_visible_or_selectable": False,
        },
        internal_capability_catalogue={
            "source": "SYSTEM_AGENT_INTERNAL_CAPABILITY_MAPPINGS",
            "count": len(internal_capability_rows),
            "all_internal_only": all(row["internal_only"] and not row["client_selectable"] for row in internal_capability_rows),
            "mapped_source_system_agent_keys": [row["source_system_agent_key"] for row in internal_capability_rows],
        },
        runtime_readiness=readiness,
        customer_safe=True,
    )
    data = result.to_dict()
    data["missing_schema_groups"] = missing_groups
    data["rds_calls_started"] = False
    data["stripe_calls_started"] = False
    data["provider_calls_started"] = False
    data["aws_calls_started"] = False
    data["billing_credit_mutation_started"] = False
    return data


def admin_rds_schema_readiness_view(readiness_or_env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    readiness = (
        dict(readiness_or_env or {})
        if "schema_inventory" in dict(readiness_or_env or {})
        else build_rds_postgres_schema_readiness(readiness_or_env)
    )
    return {
        **readiness,
        "customer_safe": True,
        "credential_values_exposed": False,
        "secret_values_visible": False,
    }


def client_rds_schema_readiness_view(readiness_or_env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    readiness = (
        dict(readiness_or_env or {})
        if "schema_inventory" in dict(readiness_or_env or {})
        else build_rds_postgres_schema_readiness(readiness_or_env)
    )
    return {
        "status": "database_schema_planned",
        "message": "Durable database readiness is being prepared.",
        "table_coverage_complete": bool(readiness.get("table_coverage_complete")),
        "customer_safe": True,
        "credential_values_exposed": False,
        "secret_values_visible": False,
        "internal_config_exposed": False,
    }
