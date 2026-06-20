export type IntegrationConnectionCategory =
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
