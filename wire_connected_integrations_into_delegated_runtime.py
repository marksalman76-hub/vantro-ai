from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
runtime_file = ROOT / "backend" / "app" / "runtime" / "delegated_workforce_execution_runtime.py"

backup_dir = ROOT / "backups" / f"delegated_runtime_connected_integrations_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(runtime_file, backup_dir / runtime_file.name)

content = runtime_file.read_text(encoding="utf-8")

old_signature = '''def execute_delegated_workforce_plan(
    *,
    implementation_plan: Dict[str, Any],
    owner_approved: bool = False,
    client_owned_agents: List[str] | None = None,
    package_tier: str = "starter",
) -> Dict[str, Any]:
'''

new_signature = '''def execute_delegated_workforce_plan(
    *,
    implementation_plan: Dict[str, Any],
    owner_approved: bool = False,
    client_owned_agents: List[str] | None = None,
    package_tier: str = "starter",
    connected_integrations: List[str] | None = None,
) -> Dict[str, Any]:
'''

if old_signature not in content:
    raise SystemExit("FUNCTION_SIGNATURE_NOT_FOUND")

content = content.replace(old_signature, new_signature)

old_client_owned = '''    client_owned_agents = client_owned_agents or []
'''

new_client_owned = '''    client_owned_agents = client_owned_agents or []
    connected_integrations = connected_integrations or []
'''

if old_client_owned not in content:
    raise SystemExit("CLIENT_OWNED_INIT_NOT_FOUND")

content = content.replace(old_client_owned, new_client_owned, 1)

old_router_call = '''            owner_approved=owner_approved,
        )
'''

new_router_call = '''            owner_approved=owner_approved,
            connected_integrations=connected_integrations,
        )
'''

if old_router_call not in content:
    raise SystemExit("ROUTER_CALL_MARKER_NOT_FOUND")

content = content.replace(old_router_call, new_router_call, 1)

old_return = '''        "enterprise_access": enterprise_access,
        "customer_safe": True,
'''

new_return = '''        "enterprise_access": enterprise_access,
        "connected_integrations": connected_integrations,
        "external_integration_count": len(connected_integrations),
        "customer_safe": True,
'''

if old_return not in content:
    raise SystemExit("RETURN_CONNECTED_MARKER_NOT_FOUND")

content = content.replace(old_return, new_return)

runtime_file.write_text(content, encoding="utf-8")

router_file = ROOT / "backend" / "app" / "runtime" / "autonomous_governed_action_router.py"
shutil.copy2(router_file, backup_dir / router_file.name)
router = router_file.read_text(encoding="utf-8")

old_route_sig = '''def route_autonomous_governed_packet(
    packet: Dict[str, Any],
    *,
    package_tier: str = "starter",
    client_owned_agents: List[str] | None = None,
    actor_role: str = "client",
    tenant_id: str = "unknown",
    owner_approved: bool = False,
) -> Dict[str, Any]:
'''

new_route_sig = '''def route_autonomous_governed_packet(
    packet: Dict[str, Any],
    *,
    package_tier: str = "starter",
    client_owned_agents: List[str] | None = None,
    actor_role: str = "client",
    tenant_id: str = "unknown",
    owner_approved: bool = False,
    connected_integrations: List[str] | None = None,
) -> Dict[str, Any]:
'''

if old_route_sig not in router:
    raise SystemExit("ROUTER_SIGNATURE_NOT_FOUND")

router = router.replace(old_route_sig, new_route_sig)

old_execute_call = '''            tenant_id=tenant_id,
        )
'''

new_execute_call = '''            tenant_id=tenant_id,
            connected_integrations=connected_integrations or [],
        )
'''

if old_execute_call not in router:
    raise SystemExit("EXECUTE_REAL_ACTION_CALL_NOT_FOUND")

router = router.replace(old_execute_call, new_execute_call, 1)

router_file.write_text(router, encoding="utf-8")

bridge_file = ROOT / "backend" / "app" / "runtime" / "real_action_execution_bridge.py"
shutil.copy2(bridge_file, backup_dir / bridge_file.name)
bridge = bridge_file.read_text(encoding="utf-8")

old_bridge_sig = '''def execute_real_action_packet(
    packet: Dict[str, Any],
    actor_role: str = "owner_admin",
    owner_approved: bool = False,
    tenant_id: str = "owner-admin",
) -> Dict[str, Any]:
'''

new_bridge_sig = '''def execute_real_action_packet(
    packet: Dict[str, Any],
    actor_role: str = "owner_admin",
    owner_approved: bool = False,
    tenant_id: str = "owner-admin",
    connected_integrations: List[str] | None = None,
) -> Dict[str, Any]:
'''

if old_bridge_sig not in bridge:
    raise SystemExit("BRIDGE_SIGNATURE_NOT_FOUND")

bridge = bridge.replace(old_bridge_sig, new_bridge_sig)

old_adapter_call = '''        tenant_id=tenant_id,
    )
'''

new_adapter_call = '''        tenant_id=tenant_id,
        connected_integrations=connected_integrations or [],
        owner_approved=owner_approved,
    )
'''

if old_adapter_call not in bridge:
    raise SystemExit("ADAPTER_CALL_NOT_FOUND")

bridge = bridge.replace(old_adapter_call, new_adapter_call, 1)

bridge_file.write_text(bridge, encoding="utf-8")

test_file = ROOT / "test_connected_integrations_delegated_runtime.py"
test_file.write_text(r'''
from backend.app.runtime.delegated_workforce_execution_runtime import execute_delegated_workforce_plan

plan = {
    "action_packets": [
        {
            "packet_id": "external_connected_001",
            "recommended_agent": "marketing_specialist_agent",
            "title": "Commission targeted healthcare technology market research and client interviews",
            "risk_level": "medium",
            "approval_required": False,
        }
    ]
}

result = execute_delegated_workforce_plan(
    implementation_plan=plan,
    owner_approved=False,
    client_owned_agents=["marketing_specialist_agent"],
    package_tier="enterprise",
    connected_integrations=["email", "crm", "calendar"],
)

assert result["success"] is True
assert result["external_integration_count"] == 3
assert result["completed_count"] == 1

completed = result["completed_results"][0]
assert completed["performed_actual_action"] is True
assert completed["deliverable"]["actions_performed"]
assert completed["deliverable"]["adapter"] == "stakeholder_interview_outreach_adapter"

# External readiness/bridge values live inside deliverable/action result chain.
assert completed["external_action_performed"] is True
assert completed["live_external_call_executed"] is True

print("CONNECTED_INTEGRATIONS_DELEGATED_RUNTIME_TEST_PASSED")
''', encoding="utf-8")

print("CONNECTED_INTEGRATIONS_WIRED_INTO_DELEGATED_RUNTIME")
print(f"Backup: {backup_dir}")
print(f"Updated: {runtime_file}")
print(f"Updated: {router_file}")
print(f"Updated: {bridge_file}")
print(f"Created: {test_file}")