from pathlib import Path
import re

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend" / "src" / "lib" / "salesDemoLaunchFlow.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "sales-demo-launch-flow-status" / "route.ts",
]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

lib_text = required_files[0].read_text(encoding="utf-8")

required_markers = [
    "sales_flow_enabled",
    "demo_flow_enabled",
    "package_positioning_ready",
    "client_safe_demo_enabled",
    "lead_capture_ready",
    "owner_follow_up_required",
    "subscription_path_visible",
    "enterprise_contact_path_visible",
    "credential_values_exposed: false",
    "external_actions_performed: false",
    "landing_page",
    "signup_flow",
    "demo_flow",
    "billing_flow",
    "activation_flow",
    "client_workspace",
    "support_flow",
]

for marker in required_markers:
    if marker not in lib_text:
        raise AssertionError(f"Missing sales/demo launch marker: {marker}")

if re.search(r"credential_values_exposed:\s*true", lib_text):
    raise AssertionError("Credential exposure violation found")

if re.search(r"external_actions_performed:\s*true", lib_text):
    raise AssertionError("External action execution violation found")

route_text = required_files[1].read_text(encoding="utf-8")

if "getSalesDemoLaunchFlowStatus" not in route_text:
    raise AssertionError("Sales/demo launch route must expose status function")

print("ROW21_SALES_DEMO_LAUNCH_FLOW_PASSED")
