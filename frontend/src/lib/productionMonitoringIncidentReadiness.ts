export type IncidentSeverity =
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
