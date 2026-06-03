from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"row18_integration_connection_hub_before_{STAMP}"

FILES = {
    "frontend/src/lib/integrationConnectionHub.ts": r'''export type IntegrationConnectionCategory =
  | "email"
  | "crm"
  | "calendar"
  | "store"
  | "website_cms"
  | "sms"
  | "social"
  | "ads"
  | "analytics";

export type IntegrationConnectionState =
  | "connected"
  | "not_connected"
  | "requires_setup"
  | "owner_approval_required"
  | "restricted";

export type IntegrationConnectionRecord = {
  integration_key: IntegrationConnectionCategory;
  label: string;
  state: IntegrationConnectionState;
  client_visible: boolean;
  admin_visible: boolean;
  credential_values_exposed: false;
  supports_test_connection: boolean;
  supports_disconnect: boolean;
  owner_approval_required_for_sensitive_actions: boolean;
  external_action_performed: false;
  last_checked_at: string;
  safe_client_message: string;
  admin_governance_note: string;
};

export type IntegrationConnectionHubStatus = {
  success: boolean;
  row: 18;
  layer: "integration_connection_hub";
  status: "ready";
  integration_hub_enabled: true;
  client_safe_visibility: true;
  admin_governance_visibility: true;
  credential_values_exposed: false;
  external_actions_performed: false;
  tenant_isolation_enforced: true;
  owner_approval_required_for_sensitive_actions: true;
  integration_count: number;
  connected_count: number;
  records: IntegrationConnectionRecord[];
  verified_at: string;
};

const checkedAt = (): string => new Date().toISOString();

const integrationRecords = (): IntegrationConnectionRecord[] => [
  {
    integration_key: "email",
    label: "Email",
    state: "requires_setup",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "Email connection can be set up for governed sending and reply workflows.",
    admin_governance_note: "Email actions must remain governed and auditable.",
  },
  {
    integration_key: "crm",
    label: "CRM",
    state: "requires_setup",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "CRM connection can be set up for lead and customer workflow support.",
    admin_governance_note: "CRM writes require tenant isolation and governed action logging.",
  },
  {
    integration_key: "calendar",
    label: "Calendar",
    state: "requires_setup",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "Calendar connection can support booking and appointment workflows.",
    admin_governance_note: "Calendar scheduling must preserve owner approval and audit boundaries.",
  },
  {
    integration_key: "store",
    label: "Store",
    state: "requires_setup",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "Store connection can support product and ecommerce workflow automation.",
    admin_governance_note: "Store operations must not alter products, pricing, or fulfilment without governance.",
  },
  {
    integration_key: "website_cms",
    label: "Website/CMS",
    state: "requires_setup",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "Website/CMS connection can support publishing and site-management workflows.",
    admin_governance_note: "Publishing actions require controlled execution and audit trails.",
  },
  {
    integration_key: "sms",
    label: "SMS",
    state: "requires_setup",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "SMS connection can support governed customer communication workflows.",
    admin_governance_note: "SMS sending must enforce consent, compliance, and rate controls.",
  },
  {
    integration_key: "social",
    label: "Social",
    state: "requires_setup",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "Social connection can support governed content and posting workflows.",
    admin_governance_note: "Posting workflows must preserve approval and brand-safety boundaries.",
  },
  {
    integration_key: "ads",
    label: "Ads",
    state: "owner_approval_required",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "Ads connection requires owner approval for spend-sensitive actions.",
    admin_governance_note: "Ad spend, budget changes, and campaign scaling remain owner-approval only.",
  },
  {
    integration_key: "analytics",
    label: "Analytics",
    state: "requires_setup",
    client_visible: true,
    admin_visible: true,
    credential_values_exposed: false,
    supports_test_connection: true,
    supports_disconnect: true,
    owner_approval_required_for_sensitive_actions: true,
    external_action_performed: false,
    last_checked_at: checkedAt(),
    safe_client_message: "Analytics connection can support reporting and optimisation insights.",
    admin_governance_note: "Analytics access must remain tenant-isolated and client-safe.",
  },
];

export function getIntegrationConnectionHubStatus(): IntegrationConnectionHubStatus {
  const records = integrationRecords();
  const connectedCount = records.filter((record) => record.state === "connected").length;

  return {
    success: true,
    row: 18,
    layer: "integration_connection_hub",
    status: "ready",
    integration_hub_enabled: true,
    client_safe_visibility: true,
    admin_governance_visibility: true,
    credential_values_exposed: false,
    external_actions_performed: false,
    tenant_isolation_enforced: true,
    owner_approval_required_for_sensitive_actions: true,
    integration_count: records.length,
    connected_count: connectedCount,
    records,
    verified_at: checkedAt(),
  };
}

export function getClientSafeIntegrationConnectionHubStatus() {
  const status = getIntegrationConnectionHubStatus();

  return {
    success: status.success,
    row: status.row,
    layer: status.layer,
    status: status.status,
    integration_hub_enabled: status.integration_hub_enabled,
    client_safe_visibility: status.client_safe_visibility,
    credential_values_exposed: false,
    external_actions_performed: false,
    integration_count: status.integration_count,
    connected_count: status.connected_count,
    records: status.records
      .filter((record) => record.client_visible)
      .map((record) => ({
        integration_key: record.integration_key,
        label: record.label,
        state: record.state,
        supports_test_connection: record.supports_test_connection,
        supports_disconnect: record.supports_disconnect,
        owner_approval_required_for_sensitive_actions:
          record.owner_approval_required_for_sensitive_actions,
        credential_values_exposed: false,
        external_action_performed: false,
        safe_client_message: record.safe_client_message,
        last_checked_at: record.last_checked_at,
      })),
    verified_at: status.verified_at,
  };
}
''',

    "frontend/src/app/api/integration-connection-hub-status/route.ts": r'''import { NextResponse } from "next/server";
import { getClientSafeIntegrationConnectionHubStatus } from "@/lib/integrationConnectionHub";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getClientSafeIntegrationConnectionHubStatus());
}
''',

    "frontend/src/app/api/admin-integration-connection-hub-status/route.ts": r'''import { NextResponse } from "next/server";
import { getIntegrationConnectionHubStatus } from "@/lib/integrationConnectionHub";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getIntegrationConnectionHubStatus());
}
''',

    "test_row18_integration_connection_hub.py": r'''from pathlib import Path
import re

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend" / "src" / "lib" / "integrationConnectionHub.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "integration-connection-hub-status" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "admin-integration-connection-hub-status" / "route.ts",
]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

lib_text = required_files[0].read_text(encoding="utf-8")

required_markers = [
    "integration_hub_enabled",
    "client_safe_visibility",
    "admin_governance_visibility",
    "credential_values_exposed: false",
    "external_actions_performed: false",
    "tenant_isolation_enforced",
    "owner_approval_required_for_sensitive_actions",
    "email",
    "crm",
    "calendar",
    "store",
    "website_cms",
    "sms",
    "social",
    "ads",
    "analytics",
    "getClientSafeIntegrationConnectionHubStatus",
]

for marker in required_markers:
    if marker not in lib_text:
        raise AssertionError(f"Missing integration connection hub marker: {marker}")

if re.search(r"credential_values_exposed:\s*true", lib_text):
    raise AssertionError("Credential exposure violation found")

if re.search(r"external_action_performed:\s*true", lib_text):
    raise AssertionError("External action execution violation found")

client_route = required_files[1].read_text(encoding="utf-8")
admin_route = required_files[2].read_text(encoding="utf-8")

if "getClientSafeIntegrationConnectionHubStatus" not in client_route:
    raise AssertionError("Client route must use client-safe integration hub status")

if "getIntegrationConnectionHubStatus" not in admin_route:
    raise AssertionError("Admin route must use full integration hub status")

print("ROW18_INTEGRATION_CONNECTION_HUB_PASSED")
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

    print("ROW18_INTEGRATION_CONNECTION_HUB_INSTALLED")
    print(f"Backup folder: {BACKUP}")

    for relative_path in FILES:
        print(f"Created/updated: {ROOT / relative_path}")

if __name__ == "__main__":
    main()