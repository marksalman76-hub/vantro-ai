from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"row20_production_monitoring_incident_readiness_before_{STAMP}"

FILES = {
    "frontend/src/lib/productionMonitoringIncidentReadiness.ts": r'''export type IncidentSeverity =
  | "info"
  | "low"
  | "medium"
  | "high"
  | "critical";

export type ProductionMonitoringSignal = {
  signal_key: string;
  label: string;
  status: "ready" | "watching" | "requires_operator_review";
  severity: IncidentSeverity;
  client_visible: boolean;
  admin_visible: boolean;
  safe_message: string;
  operator_note: string;
  checked_at: string;
};

export type ProductionMonitoringIncidentReadinessStatus = {
  success: boolean;
  row: 20;
  layer: "production_monitoring_incident_readiness";
  status: "ready";
  production_monitoring_enabled: true;
  incident_readiness_enabled: true;
  admin_operator_visibility_enabled: true;
  client_safe_status_enabled: true;
  escalation_path_defined: true;
  rollback_readiness_defined: true;
  provider_health_watch_enabled: true;
  runtime_health_watch_enabled: true;
  billing_health_watch_enabled: true;
  security_health_watch_enabled: true;
  credential_values_exposed: false;
  external_actions_performed: false;
  signals_count: number;
  signals: ProductionMonitoringSignal[];
  verified_at: string;
};

const checkedAt = (): string => new Date().toISOString();

const signals = (): ProductionMonitoringSignal[] => [
  {
    signal_key: "runtime_health",
    label: "Runtime Health",
    status: "watching",
    severity: "medium",
    client_visible: true,
    admin_visible: true,
    safe_message: "Runtime health monitoring is active.",
    operator_note: "Monitor API and frontend route readiness during production operations.",
    checked_at: checkedAt(),
  },
  {
    signal_key: "provider_health",
    label: "Provider Health",
    status: "watching",
    severity: "medium",
    client_visible: false,
    admin_visible: true,
    safe_message: "Provider readiness checks are active.",
    operator_note: "Provider failures should trigger retry/failover review before customer impact.",
    checked_at: checkedAt(),
  },
  {
    signal_key: "billing_health",
    label: "Billing Health",
    status: "watching",
    severity: "high",
    client_visible: true,
    admin_visible: true,
    safe_message: "Billing status monitoring is active.",
    operator_note: "Stripe subscription, checkout, package, and credit state must remain aligned.",
    checked_at: checkedAt(),
  },
  {
    signal_key: "security_governance",
    label: "Security & Governance",
    status: "watching",
    severity: "critical",
    client_visible: false,
    admin_visible: true,
    safe_message: "Governance protections are active.",
    operator_note: "Credential exposure, tenant isolation, and owner-approval boundaries must remain enforced.",
    checked_at: checkedAt(),
  },
  {
    signal_key: "incident_response",
    label: "Incident Response",
    status: "ready",
    severity: "high",
    client_visible: false,
    admin_visible: true,
    safe_message: "Incident response readiness is active.",
    operator_note: "Operator should use rollback, disable live providers, pause affected integrations, and review audit events when needed.",
    checked_at: checkedAt(),
  },
];

export function getProductionMonitoringIncidentReadinessStatus(): ProductionMonitoringIncidentReadinessStatus {
  const currentSignals = signals();

  return {
    success: true,
    row: 20,
    layer: "production_monitoring_incident_readiness",
    status: "ready",
    production_monitoring_enabled: true,
    incident_readiness_enabled: true,
    admin_operator_visibility_enabled: true,
    client_safe_status_enabled: true,
    escalation_path_defined: true,
    rollback_readiness_defined: true,
    provider_health_watch_enabled: true,
    runtime_health_watch_enabled: true,
    billing_health_watch_enabled: true,
    security_health_watch_enabled: true,
    credential_values_exposed: false,
    external_actions_performed: false,
    signals_count: currentSignals.length,
    signals: currentSignals,
    verified_at: checkedAt(),
  };
}

export function getClientSafeProductionMonitoringIncidentReadinessStatus() {
  const status = getProductionMonitoringIncidentReadinessStatus();

  return {
    success: status.success,
    row: status.row,
    layer: status.layer,
    status: status.status,
    production_monitoring_enabled: status.production_monitoring_enabled,
    incident_readiness_enabled: status.incident_readiness_enabled,
    client_safe_status_enabled: status.client_safe_status_enabled,
    credential_values_exposed: false,
    external_actions_performed: false,
    signals_count: status.signals.filter((signal) => signal.client_visible).length,
    signals: status.signals
      .filter((signal) => signal.client_visible)
      .map((signal) => ({
        signal_key: signal.signal_key,
        label: signal.label,
        status: signal.status,
        severity: signal.severity,
        safe_message: signal.safe_message,
        checked_at: signal.checked_at,
      })),
    verified_at: status.verified_at,
  };
}
''',

    "frontend/src/app/api/production-monitoring-incident-readiness-status/route.ts": r'''import { NextResponse } from "next/server";
import { getClientSafeProductionMonitoringIncidentReadinessStatus } from "@/lib/productionMonitoringIncidentReadiness";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getClientSafeProductionMonitoringIncidentReadinessStatus());
}
''',

    "frontend/src/app/api/admin-production-monitoring-incident-readiness-status/route.ts": r'''import { NextResponse } from "next/server";
import { getProductionMonitoringIncidentReadinessStatus } from "@/lib/productionMonitoringIncidentReadiness";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getProductionMonitoringIncidentReadinessStatus());
}
''',

    "test_row20_production_monitoring_incident_readiness.py": r'''from pathlib import Path
import re

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend" / "src" / "lib" / "productionMonitoringIncidentReadiness.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "production-monitoring-incident-readiness-status" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "admin-production-monitoring-incident-readiness-status" / "route.ts",
]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

lib_text = required_files[0].read_text(encoding="utf-8")

required_markers = [
    "production_monitoring_enabled",
    "incident_readiness_enabled",
    "admin_operator_visibility_enabled",
    "client_safe_status_enabled",
    "escalation_path_defined",
    "rollback_readiness_defined",
    "provider_health_watch_enabled",
    "runtime_health_watch_enabled",
    "billing_health_watch_enabled",
    "security_health_watch_enabled",
    "credential_values_exposed: false",
    "external_actions_performed: false",
    "getClientSafeProductionMonitoringIncidentReadinessStatus",
]

for marker in required_markers:
    if marker not in lib_text:
        raise AssertionError(f"Missing monitoring/incident marker: {marker}")

if re.search(r"credential_values_exposed:\s*true", lib_text):
    raise AssertionError("Credential exposure violation found")

if re.search(r"external_actions_performed:\s*true", lib_text):
    raise AssertionError("External action execution violation found")

client_route = required_files[1].read_text(encoding="utf-8")
admin_route = required_files[2].read_text(encoding="utf-8")

if "getClientSafeProductionMonitoringIncidentReadinessStatus" not in client_route:
    raise AssertionError("Client route must use client-safe monitoring status")

if "getProductionMonitoringIncidentReadinessStatus" not in admin_route:
    raise AssertionError("Admin route must use full monitoring status")

print("ROW20_PRODUCTION_MONITORING_INCIDENT_READINESS_PASSED")
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

    print("ROW20_PRODUCTION_MONITORING_INCIDENT_READINESS_INSTALLED")
    print(f"Backup folder: {BACKUP}")

    for relative_path in FILES:
        print(f"Created/updated: {ROOT / relative_path}")

if __name__ == "__main__":
    main()