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


def main() -> int:
    adapter = load_module(
        "backend/app/runtime/durable_media_job_status_adapter.py",
        "durable_media_job_status_adapter_under_test",
    )
    aws_contract = load_module(
        "backend/app/runtime/aws_option_a_runtime_contract.py",
        "aws_option_a_runtime_contract_for_status_adapter_test",
    )
    source = read("backend/app/runtime/durable_media_job_status_adapter.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    sample_payload = {
        "job_id": "job_aws02_test",
        "client_id": "client_123",
        "tenant_id": "tenant_123",
        "status": "universal_complete_media_visual_failed",
        "client_safe_status": "needs_attention",
        "media_type": "complete_video",
        "asset_type": "final_mp4",
        "selected_agent": "creative_director_agent",
        "selected_agents": ["creative_director_agent", "media_producer_agent"],
        "agent_ids": ["creative_director_agent", "media_producer_agent"],
        "multi_agent_media_execution": True,
        "video_provider": "runway",
        "audio_provider": "elevenlabs",
        "provider_job_id": "runway_job_123",
        "provider_attempt_count": 2,
        "safe_error_summary": "Runway provider attempt failed before final video delivery.",
        "provider_diagnostics": {
            "provider": "runway",
            "safe_error_summary": "provider_execution_error",
            "runway_api_key": "RUNWAY_SECRET_SHOULD_NOT_LEAK",
            "request_headers": {"Authorization": "Bearer SHOULD_NOT_LEAK"},
        },
        "internal_config": {
            "DATABASE_URL": "postgres://SHOULD_NOT_LEAK",
        },
        "estimated_credit_risk": {
            "risk_level": "low",
            "paid_visual_provider_attempts_possible": 1,
            "paid_audio_provider_attempts_possible": 1,
        },
        "assets": [
            {
                "asset_type": "preview_video",
                "storage_key": "media/job_aws02_test/preview.mp4",
                "preview_url": "/api/universal-complete-media-asset?id=asset_1",
            }
        ],
        "created_at": "2026-06-15T00:00:00+00:00",
        "updated_at": "2026-06-15T00:01:00+00:00",
    }

    record = adapter.build_durable_media_job_status_record(sample_payload)
    admin_view = adapter.build_admin_media_job_status_view(record)
    client_view = adapter.build_client_media_job_status_view(record)
    client_text = str(client_view)
    admin_text = str(admin_view)

    for key in [
        "job_id",
        "customer_id",
        "client_safe_status",
        "internal_status",
        "media_type",
        "asset_type",
        "selected_agent",
        "selected_agents",
        "agent_ids",
        "multi_agent_media_execution",
        "provider_summary",
        "provider_attempt_count",
        "asset_references",
        "error_summary",
        "diagnostics_visibility_rules",
        "credit_billing",
        "created_at",
        "updated_at",
    ]:
        require(key in record, f"Canonical durable record missing field: {key}")

    require(record["job_id"] == "job_aws02_test", "Record must preserve job_id.")
    require(record["customer_id"] == "client_123", "Record must map client_id/customer_id.")
    require(record["selected_agent"] == "creative_director_agent", "Record must preserve selected_agent.")
    require(record["selected_agents"] == sample_payload["selected_agents"], "Record must preserve selected_agents.")
    require(record["agent_ids"] == sample_payload["agent_ids"], "Record must preserve agent_ids.")
    require(record["multi_agent_media_execution"] is True, "Record must preserve multi-agent execution marker.")
    require(record["provider_attempt_count"] == 2, "Provider attempt count must be preserved.")

    require("provider_diagnostics" in admin_view, "Admin view must include provider diagnostics.")
    require("internal_status" in admin_view, "Admin view must include internal status.")
    require(admin_view["provider_summary"]["video_provider"] == "runway", "Admin provider summary must include provider name.")
    require("RUNWAY_SECRET_SHOULD_NOT_LEAK" not in admin_text, "Admin view must redact provider secret values.")
    require("SHOULD_NOT_LEAK" not in admin_text, "Admin view must redact secret-like values.")

    for hidden_key in [
        "provider_diagnostics",
        "internal_diagnostics",
        "internal_status",
        "internal_config",
        "provider_summary",
        "credit_billing",
    ]:
        require(hidden_key not in client_view, f"Client view must hide {hidden_key}.")
    require(client_view["status"] == "needs_attention", "Client view must expose only client-safe status.")
    require(client_view["customer_safe"] is True, "Client view must be customer_safe.")
    require(client_view["credential_values_exposed"] is False, "Client view must not expose credentials.")
    require("RUNWAY_SECRET_SHOULD_NOT_LEAK" not in client_text, "Client view leaked provider secret.")
    require("provider_execution_error" not in client_text, "Client view leaked internal provider diagnostic.")

    local_contract = aws_contract.aws_option_a_readiness({})
    require(local_contract["aws_option_a_enabled"] is False, "AWS Option A must remain disabled by default.")
    require(local_contract["ready_for_aws_execution"] is False, "AWS/RDS credentials must not be required for AWS-02 local mapping.")
    require(record["aws_rds_required"] is False, "AWS-02 adapter must not require RDS credentials yet.")

    for marker in [
        "DurableMediaJobStatusRecord",
        "build_durable_media_job_status_record",
        "build_admin_media_job_status_view",
        "build_client_media_job_status_view",
        "map_media_job_status_for_portal",
        "client_view_hides_provider_diagnostics",
        "secret_values_always_redacted",
    ]:
        require(marker in source, f"Adapter source missing marker: {marker}")

    for marker in [
        "AWS-02",
        "durable status adapter boundary",
        "verify_durable_media_job_status_adapter.py",
        "client-safe job status view",
        "admin-safe job status view",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-02 marker: {marker}")

    print("DURABLE_MEDIA_JOB_STATUS_ADAPTER_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
