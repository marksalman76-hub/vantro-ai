from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

path = ROOT / "backend" / "app" / "runtime" / "execution_stack.py"
backup = BACKUPS / f"execution_stack_before_step_t_live_adapter_bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

s = path.read_text(encoding="utf-8", errors="ignore")

if "from backend.app.core.integration_live_adapter_registry import execute_integration_action" not in s:
    s = s.replace(
        "from backend.app.integrations.execution_adapters import ExecutionAdapters, adapter_summary",
        "from backend.app.integrations.execution_adapters import ExecutionAdapters, adapter_summary\nfrom backend.app.core.integration_live_adapter_registry import execute_integration_action",
    )

s = s.replace(
    '''SUPPORTED_EXECUTION_ACTIONS = [''',
    '''SUPPORTED_EXECUTION_ACTIONS = [''',
)

if '"execute_live_integration_action",' not in s:
    s = s.replace(
        "SUPPORTED_EXECUTION_ACTIONS = [",
        'SUPPORTED_EXECUTION_ACTIONS = [\n    "execute_live_integration_action",',
        1,
    )

old = '''        adapter = self._select_adapter(request.action_type)
        adapter_result = self.adapters.execute(adapter, request.payload)
        adapter_result_data = adapter_summary(adapter_result)
'''

new = '''        if request.action_type == "execute_live_integration_action":
            live_result = execute_integration_action(
                tenant_id=str(request.payload.get("tenant_id") or "client_demo_001"),
                integration_key=str(request.payload.get("integration_key") or ""),
                action=str(request.payload.get("action") or ""),
                payload=dict(request.payload.get("payload") or {}),
                actor_role=str(request.payload.get("actor_role") or "customer"),
            )
            return ExecutionResult(
                success=bool(live_result.get("success")),
                execution_status="live_integration_action_executed" if live_result.get("success") else "live_integration_action_failed",
                action_type=request.action_type,
                message="Live integration action routed through governed global adapter registry.",
                execution_notes=[
                    "Global integration adapter registry used.",
                    "Credential exposure blocked.",
                    "Owner approval protections remain enforced by adapter registry.",
                ],
                adapter="global_integration_live_adapter_registry",
                adapter_result=live_result,
            )

        adapter = self._select_adapter(request.action_type)
        adapter_result = self.adapters.execute(adapter, request.payload)
        adapter_result_data = adapter_summary(adapter_result)
'''

if old not in s:
    raise SystemExit("EXECUTION_STACK_ADAPTER_BLOCK_NOT_FOUND")

s = s.replace(old, new, 1)

path.write_text(s, encoding="utf-8")

test = ROOT / "test_step_t_execution_stack_live_adapter_bridge.py"
test.write_text(r'''from backend.app.runtime.execution_stack import ExecutionStack, ExecutionRequest, execution_summary

stack = ExecutionStack()

result = stack.route(
    ExecutionRequest(
        action_type="execute_live_integration_action",
        payload={
            "tenant_id": "client_demo_001",
            "integration_key": "crm",
            "action": "add_note",
            "actor_role": "customer",
            "payload": {
                "location_id": "mlWJi2CdN2cXHRe06d5b",
                "contact_id": "REPLACE_WITH_EXISTING_GHL_CONTACT_ID",
                "body": "ExecutionStack bridge proof: agent runtime can route to live CRM adapter safely.",
            },
        },
        owner_approved=False,
    )
)

print(execution_summary(result))
''', encoding="utf-8")

print("STEP_T_EXECUTION_STACK_LIVE_ADAPTER_BRIDGE_INSTALLED")
print(f"Backup: {backup}")