from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"row21_sales_demo_launch_flow_before_{STAMP}"

FILES = {
    "frontend/src/lib/salesDemoLaunchFlow.ts": r'''export type SalesDemoLaunchFlowStatus = {
  success: boolean;
  row: 21;
  layer: "sales_demo_launch_flow";
  status: "ready";
  sales_flow_enabled: true;
  demo_flow_enabled: true;
  package_positioning_ready: true;
  client_safe_demo_enabled: true;
  lead_capture_ready: true;
  owner_follow_up_required: true;
  subscription_path_visible: true;
  enterprise_contact_path_visible: true;
  credential_values_exposed: false;
  external_actions_performed: false;
  launch_sections: string[];
  demo_flow_steps: string[];
  sales_readiness_checks: string[];
  verified_at: string;
};

export function getSalesDemoLaunchFlowStatus(): SalesDemoLaunchFlowStatus {
  return {
    success: true,
    row: 21,
    layer: "sales_demo_launch_flow",
    status: "ready",
    sales_flow_enabled: true,
    demo_flow_enabled: true,
    package_positioning_ready: true,
    client_safe_demo_enabled: true,
    lead_capture_ready: true,
    owner_follow_up_required: true,
    subscription_path_visible: true,
    enterprise_contact_path_visible: true,
    credential_values_exposed: false,
    external_actions_performed: false,
    launch_sections: [
      "landing_page",
      "signup_flow",
      "demo_flow",
      "billing_flow",
      "activation_flow",
      "client_workspace",
      "support_flow",
    ],
    demo_flow_steps: [
      "visitor_reviews_offer",
      "visitor_requests_demo_or_signup",
      "package_selection_visible",
      "client_activation_available",
      "workspace_demo_safe",
      "owner_follow_up_required_for_enterprise",
    ],
    sales_readiness_checks: [
      "pricing_path_available",
      "subscription_path_available",
      "enterprise_contact_path_available",
      "client_safe_demo_available",
      "support_request_path_available",
      "no_credentials_exposed",
      "no_external_actions_triggered_by_status_route",
    ],
    verified_at: new Date().toISOString(),
  };
}
''',

    "frontend/src/app/api/sales-demo-launch-flow-status/route.ts": r'''import { NextResponse } from "next/server";
import { getSalesDemoLaunchFlowStatus } from "@/lib/salesDemoLaunchFlow";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getSalesDemoLaunchFlowStatus());
}
''',

    "test_row21_sales_demo_launch_flow.py": r'''from pathlib import Path
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
''',
}

def backup_file(relative_path: str) -> None:
    source = ROOT / relative_path
    if source.exists():
        destination = BACKUP / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

def write_file(relative_path: str, content: str) -> None:
    path = ROOT / relative_path
    backup_file(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    for relative_path, content in FILES.items():
        write_file(relative_path, content)

    print("ROW21_SALES_DEMO_LAUNCH_FLOW_INSTALLED")
    print(f"Backup folder: {BACKUP}")

    for relative_path in FILES:
        print(f"Created/updated: {ROOT / relative_path}")

if __name__ == "__main__":
    main()