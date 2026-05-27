import os

from backend.app.runtime.live_provider_adapters import (
    build_failover_routing_packet,
    build_polling_packet,
    calculate_provider_health_score,
    check_provider_gate,
    create_execution_audit_linkage,
    create_signed_asset_delivery_packet,
    execute_gate_safe_provider_request,
    live_provider_adapter_runtime_status,
    normalise_provider_failure,
    provider_timeout_policy,
)


def test_openai_gate_blocks_without_credentials(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = check_provider_gate(
        "openai",
        live_execution_requested=True,
        owner_governed_execution_confirmed=True,
    )
    assert result["known_adapter"] is True
    assert result["configured"] is False
    assert result["ready"] is False
    assert result["execution_allowed"] is False
    assert "OPENAI_API_KEY" in result["missing"]
    assert result["credential_values_exposed"] is False


def test_openai_gate_blocks_without_live_request_even_with_credential(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-exposed")
    result = check_provider_gate(
        "openai",
        live_execution_requested=False,
        owner_governed_execution_confirmed=True,
    )
    assert result["configured"] is True
    assert result["execution_allowed"] is False
    assert result["reason"] == "live_execution_not_requested"
    assert result["credential_values_exposed"] is False


def test_openai_gate_blocks_without_owner_confirmation(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-exposed")
    result = check_provider_gate(
        "openai",
        live_execution_requested=True,
        owner_governed_execution_confirmed=False,
    )
    assert result["configured"] is True
    assert result["execution_allowed"] is False
    assert result["reason"] == "owner_governed_execution_not_confirmed"


def test_openai_adapter_ready_for_live_call_only_when_all_gates_pass(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-exposed")
    result = execute_gate_safe_provider_request(
        "openai",
        {
            "tenant_id": "tenant-test",
            "request_id": "request-test",
            "prompt": "Create a safe premium asset brief",
            "live_execution_requested": True,
            "owner_governed_execution_confirmed": True,
        },
    )
    assert result["status"] == "ready_for_live_provider_call"
    assert result["adapter_name"] == "openai_live_execution_adapter_v1"
    assert result["normalised_request"]["prompt_present"] is True
    assert result["credential_values_exposed"] is False


def test_unknown_provider_blocks():
    result = execute_gate_safe_provider_request("unknown-provider", {})
    assert result["status"] == "blocked"
    assert result["known_adapter"] is False
    assert result["credential_values_exposed"] is False


def test_timeout_and_polling_packet():
    policy = provider_timeout_policy("runway")
    assert policy["job_timeout_seconds"] >= 900

    packet = build_polling_packet("runway", "job-123")
    assert packet["provider_job_id"] == "job-123"
    assert "completed" in packet["status_map"]
    assert packet["credential_values_exposed"] is False


def test_failure_normalisation():
    result = normalise_provider_failure(
        "openai",
        error_code="provider_timeout",
        message="Provider timed out safely.",
        retryable=True,
        status_code=504,
    )
    assert result["status"] == "failed"
    assert result["retryable"] is True
    assert result["credential_values_exposed"] is False


def test_health_score_and_failover_packet(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-exposed")
    monkeypatch.delenv("RUNWAY_API_KEY", raising=False)

    health = calculate_provider_health_score(
        success_count=8,
        failure_count=1,
        timeout_count=1,
        average_latency_ms=35000,
    )
    assert 0 <= health["health_score"] <= 100
    assert "failover_recommended" in health

    failover = build_failover_routing_packet(
        "runway",
        available_providers=["openai", "runway"],
    )
    assert "openai" in failover["available_configured_providers"]
    assert "runway" not in failover["available_configured_providers"]
    assert failover["credential_values_exposed"] is False


def test_signed_asset_packet_and_audit_linkage(monkeypatch):
    monkeypatch.setenv("ASSET_PACKET_SIGNING_SECRET", "test-signing-secret")
    packet = create_signed_asset_delivery_packet(
        tenant_id="tenant-test",
        asset_id="asset-123",
        provider_key="openai",
        asset_type="image",
    )
    assert packet["customer_safe"] is True
    assert packet["download_allowed"] is True
    assert len(packet["signature"]) == 64
    assert packet["credential_values_exposed"] is False

    audit = create_execution_audit_linkage(
        tenant_id="tenant-test",
        request_id="request-123",
        provider_key="openai",
        provider_job_id="provider-job-123",
        execution_status="queued",
    )
    assert audit["audit_event_type"] == "provider_execution_linkage"
    assert audit["credential_values_exposed"] is False


def test_runtime_status_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    status = live_provider_adapter_runtime_status("openai")
    assert status["known_adapter"] is True
    assert status["configured"] is False
    assert status["ready"] is False
    assert "OPENAI_API_KEY" in status["missing"]
    assert status["owner_governed_execution_required"] is True
    assert status["credential_values_exposed"] is False
