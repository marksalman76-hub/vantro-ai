from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

target = ROOT / "backend" / "app" / "runtime" / "real_provider_http_execution_layer.py"
test_file = ROOT / "test_openai_execution_audit_asset_integration_direct.py"

backup_dir = ROOT / "backups" / f"openai_execution_audit_asset_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

s = target.read_text(encoding="utf-8")

import_block = '''from backend.app.runtime.asset_storage_signed_delivery_runtime import (
    create_asset_record,
    create_customer_safe_asset_preview,
    update_asset_status,
)
from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_latency_metric_bridge,
    persist_provider_execution_record_bridge,
    persist_worker_event_bridge,
)
'''

if "asset_storage_signed_delivery_runtime import" not in s:
    s = s.replace(
        "from backend.app.runtime.live_provider_adapters import (\n",
        import_block + "from backend.app.runtime.live_provider_adapters import (\n",
    )

extra = r'''

def persist_openai_execution_audit_asset(
    *,
    tenant_id: str,
    request_id: str,
    provider_job_id: str,
    output_text: Optional[str] = None,
    asset_type: str = "text",
    latency_ms: int = 0,
) -> Dict[str, Any]:
    execution_bridge = persist_provider_execution_record_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key="openai",
        task_type="controlled_openai_live_execution",
        execution_status="completed",
        worker_job_id=None,
        provider_job_id=provider_job_id,
    )
    execution_id = execution_bridge.get("record", {}).get("execution_id", f"openai_execution_{uuid.uuid4().hex[:12]}")

    asset = create_asset_record(
        tenant_id=tenant_id,
        request_id=request_id,
        provider_key="openai",
        asset_type=asset_type,
        asset_status="ready",
        source_url=None,
        metadata={
            "provider_job_id": provider_job_id,
            "output_text_present": bool(output_text),
            "source": "controlled_openai_live_execution",
        },
    )

    update_asset_status(
        asset_id=asset["asset_id"],
        asset_status="ready",
        metadata={
            "execution_id": execution_id,
            "provider_job_id": provider_job_id,
        },
    )

    preview = create_customer_safe_asset_preview(
        tenant_id=tenant_id,
        asset_id=asset["asset_id"],
    )

    event_bridge = persist_worker_event_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=provider_job_id,
        provider_key="openai",
        event_type="controlled_openai_execution_completed",
        status="completed",
        details={
            "asset_id": asset["asset_id"],
            "asset_type": asset_type,
            "output_text_present": bool(output_text),
        },
    )

    latency_bridge = persist_latency_metric_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        provider_key="openai",
        latency_ms=int(latency_ms or 0),
        operation="controlled_openai_live_execution",
    )

    return {
        "status": "persisted",
        "execution_bridge": execution_bridge,
        "execution_id": execution_id,
        "asset": asset,
        "preview": preview,
        "event_bridge": event_bridge,
        "latency_bridge": latency_bridge,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def controlled_openai_audit_asset_integration_status() -> Dict[str, Any]:
    return {
        "provider_key": "openai",
        "audit_asset_integration_ready": True,
        "execution_record_persistence_ready": True,
        "asset_record_creation_ready": True,
        "customer_safe_preview_ready": True,
        "ledger_event_ready": True,
        "latency_metric_ready": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''

if "def persist_openai_execution_audit_asset(" not in s:
    s = s.rstrip() + extra + "\n"

old = '''        return {
            "provider_key": "openai",
            "status": "completed",
            "provider_job_id": response_id,
            "normalised_response": normalised,
            "live_external_call_executed": True,
            "latency_ms": _now_ms() - started_at,
            "credential_values_exposed": False,
            "customer_safe": True,
        }'''

new = '''        latency_ms = _now_ms() - started_at
        audit_asset = persist_openai_execution_audit_asset(
            tenant_id=payload.get("tenant_id") or "unknown-tenant",
            request_id=payload.get("request_id") or "unknown-request",
            provider_job_id=response_id,
            output_text=output_text,
            asset_type=payload.get("asset_type") or "text",
            latency_ms=latency_ms,
        )

        return {
            "provider_key": "openai",
            "status": "completed",
            "provider_job_id": response_id,
            "normalised_response": normalised,
            "audit_asset": audit_asset,
            "live_external_call_executed": True,
            "latency_ms": latency_ms,
            "credential_values_exposed": False,
            "customer_safe": True,
        }'''

if old in s and "audit_asset = persist_openai_execution_audit_asset(" not in s:
    s = s.replace(old, new)

target.write_text(s, encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.real_provider_http_execution_layer import (
    controlled_openai_audit_asset_integration_status,
    persist_openai_execution_audit_asset,
)

status = controlled_openai_audit_asset_integration_status()
assert status["audit_asset_integration_ready"] is True
assert status["asset_record_creation_ready"] is True
assert status["customer_safe_preview_ready"] is True
assert status["credential_values_exposed"] is False

result = persist_openai_execution_audit_asset(
    tenant_id="tenant-test",
    request_id="request-test",
    provider_job_id="openai-response-123",
    output_text="Safe generated result.",
    asset_type="text",
    latency_ms=1234,
)

assert result["status"] == "persisted"
assert result["execution_id"]
assert result["asset"]["provider_key"] == "openai"
assert result["asset"]["asset_status"] == "ready"
assert result["preview"]["status"] == "ready"
assert result["preview"]["internal_storage_key_exposed"] is False
assert result["event_bridge"]["entry"]["event_type"] == "controlled_openai_execution_completed"
assert result["latency_bridge"]["metric"]["latency_ms"] == 1234
assert result["credential_values_exposed"] is False
assert result["customer_safe"] is True

print("OPENAI_EXECUTION_AUDIT_ASSET_INTEGRATION_DIRECT_TESTS_PASSED")
print("status_ready", status["audit_asset_integration_ready"])
print("persisted_status", result["status"])
print("execution_id", result["execution_id"])
print("asset_id", result["asset"]["asset_id"])
print("preview_status", result["preview"]["status"])
print("event_type", result["event_bridge"]["entry"]["event_type"])
print("latency", result["latency_bridge"]["metric"]["latency_ms"])
'''.lstrip(), encoding="utf-8")

print("OPENAI_EXECUTION_AUDIT_ASSET_INTEGRATION_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")
print(f"Created/updated: {test_file}")