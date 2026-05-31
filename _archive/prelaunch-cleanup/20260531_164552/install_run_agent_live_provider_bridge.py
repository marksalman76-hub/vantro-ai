from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "runtime" / "execution_stack.py"
test_file = ROOT / "test_run_agent_live_provider_bridge.py"

backup_dir = ROOT / "backups" / f"run_agent_live_provider_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

if "from backend.app.runtime.real_provider_http_execution_layer import execute_controlled_openai_live_request" not in text:
    text = text.replace(
        "from backend.app.core.integration_live_adapter_registry import execute_integration_action\n",
        "from backend.app.core.integration_live_adapter_registry import execute_integration_action\n"
        "from backend.app.runtime.real_provider_http_execution_layer import execute_controlled_openai_live_request\n",
    )

if '"governed_live_provider_generation",' not in text:
    text = text.replace(
        '    "prepare_analytics_report",\n]',
        '    "prepare_analytics_report",\n'
        '    "governed_live_provider_generation",\n'
        ']',
    )

bridge_block = '''
        if request.action_type == "governed_live_provider_generation":
            safe_payload = dict(request.payload or {})
            workflow = safe_payload.get("workflow") if isinstance(safe_payload.get("workflow"), dict) else {}
            output = safe_payload.get("output") if isinstance(safe_payload.get("output"), dict) else {}
            requested_prompt = (
                safe_payload.get("prompt")
                or safe_payload.get("task")
                or workflow.get("task")
                or output.get("generated_output")
                or output.get("output")
                or output.get("content")
                or output.get("deliverable")
                or "Generate a concise customer-safe execution result."
            )

            live_result = execute_controlled_openai_live_request({
                "tenant_id": request.tenant_id,
                "request_id": str(safe_payload.get("request_id") or f"run_agent_{request.tenant_id}_governed_live_provider_generation"),
                "prompt": str(requested_prompt),
                "asset_type": "text",
                "live_execution_requested": True,
                "owner_governed_execution_confirmed": bool(request.owner_approved),
            })

            completed = bool(live_result.get("status") == "completed" and live_result.get("live_external_call_executed") is True)

            return ExecutionResult(
                success=completed,
                execution_status="governed_live_provider_execution_completed" if completed else "governed_live_provider_execution_not_completed",
                action_type=request.action_type,
                message="Governed live provider execution routed through verified OpenAI provider bridge." if completed else "Governed live provider execution did not complete.",
                execution_notes=[
                    "Owner approval, quality gate, provider dispatch policy, credential protection, and durable audit persistence remain enforced.",
                    "No client credit/package/entitlement limits are applied to owner/admin internal execution.",
                    "Provider credential values are never exposed.",
                    "External execution only occurs when final provider network gates are enabled and owner-governed execution is confirmed.",
                ],
                adapter="governed_openai_live_provider_bridge",
                adapter_result={
                    "success": completed,
                    "provider_key": "openai",
                    "status": live_result.get("status"),
                    "provider_job_id": live_result.get("provider_job_id"),
                    "live_external_call_executed": bool(live_result.get("live_external_call_executed")),
                    "latency_ms": live_result.get("latency_ms"),
                    "normalised_response": live_result.get("normalised_response"),
                    "audit_asset": live_result.get("audit_asset"),
                    "credential_values_exposed": bool(live_result.get("credential_values_exposed")),
                    "customer_safe": bool(live_result.get("customer_safe", True)),
                },
            )

'''

if 'if request.action_type == "governed_live_provider_generation":' not in text:
    marker = '        if request.action_type == "execute_live_integration_action":\n'
    if marker not in text:
        raise SystemExit("Could not find execute_live_integration_action block marker")
    text = text.replace(marker, bridge_block + marker)

target.write_text(text, encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.execution_stack import ExecutionRequest, ExecutionStack


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


stack = ExecutionStack()

blocked_quality = stack.route(ExecutionRequest(
    tenant_id="owner_admin",
    action_type="governed_live_provider_generation",
    payload={"prompt": "Return bridge test."},
    owner_approved=True,
    quality_passed=False,
))
assert_true(blocked_quality.success is False, "quality gate must still block")
assert_true(blocked_quality.execution_status == "blocked_quality_gate_required", "quality gate status mismatch")

blocked_approval = stack.route(ExecutionRequest(
    tenant_id="owner_admin",
    action_type="launch_paid_campaign",
    payload={"prompt": "Do not launch."},
    owner_approved=False,
    quality_passed=True,
))
assert_true(blocked_approval.success is False, "spend action must still block without owner approval")
assert_true(blocked_approval.execution_status == "blocked_pending_owner_approval", "approval block status mismatch")

bridge = stack.route(ExecutionRequest(
    tenant_id="owner_admin",
    action_type="governed_live_provider_generation",
    payload={
        "request_id": "local_bridge_test_no_external_expectation",
        "prompt": "Local bridge test. External execution depends on environment gates.",
    },
    owner_approved=True,
    quality_passed=True,
))

assert_true(bridge.action_type == "governed_live_provider_generation", "bridge action mismatch")
assert_true(bridge.adapter == "governed_openai_live_provider_bridge", "bridge adapter mismatch")
assert_true(bridge.adapter_result is not None, "bridge adapter result missing")
assert_true(bridge.adapter_result.get("credential_values_exposed") is False, "credentials exposed")
assert_true(bridge.adapter_result.get("customer_safe") is True, "bridge result not customer safe")
assert_true(bridge.execution_status in {
    "governed_live_provider_execution_completed",
    "governed_live_provider_execution_not_completed",
}, "unexpected bridge status")

print("RUN_AGENT_LIVE_PROVIDER_BRIDGE_TEST_PASSED")
print({
    "quality_block": blocked_quality.execution_status,
    "approval_block": blocked_approval.execution_status,
    "bridge_status": bridge.execution_status,
    "bridge_adapter": bridge.adapter,
    "live_external_call_executed": bridge.adapter_result.get("live_external_call_executed"),
})
'''.lstrip(), encoding="utf-8")

print("RUN_AGENT_LIVE_PROVIDER_BRIDGE_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")
print(f"Created/updated: {test_file}")