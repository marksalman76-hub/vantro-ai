from pathlib import Path
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
