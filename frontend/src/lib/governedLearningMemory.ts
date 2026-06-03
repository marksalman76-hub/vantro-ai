export type GovernedLearningMemoryScope =
  | "owner_admin"
  | "client_workspace"
  | "agent_runtime"
  | "quality_loop"
  | "deliverable_feedback";

export type GovernedLearningMemorySensitivity =
  | "public_safe"
  | "client_safe"
  | "admin_only"
  | "proprietary_internal";

export type GovernedLearningMemoryRecord = {
  memory_id: string;
  tenant_id: string;
  client_display_name: string;
  agent_key: string;
  source_scope: GovernedLearningMemoryScope;
  sensitivity: GovernedLearningMemorySensitivity;
  memory_type: string;
  summary: string;
  safe_client_summary: string;
  learning_signal: string;
  quality_signal: "positive" | "neutral" | "negative" | "needs_review";
  owner_approved: boolean;
  client_visible: boolean;
  proprietary_logic_exposed: boolean;
  created_at: string;
  updated_at: string;
};

export type GovernedLearningMemoryStatus = {
  success: boolean;
  row: 16;
  layer: "governed_learning_memory";
  status: "ready";
  governed_memory_enabled: true;
  client_safe_visibility: true;
  proprietary_logic_hidden_from_clients: true;
  owner_admin_diagnostics_enabled: true;
  no_autonomous_retraining: true;
  owner_approval_required_for_learning_policy_changes: true;
  tenant_isolation_enforced: true;
  memory_record_count: number;
  records: GovernedLearningMemoryRecord[];
  client_safe_records: GovernedLearningMemoryRecord[];
};

const nowIso = (): string => new Date().toISOString();

const baseRecords: GovernedLearningMemoryRecord[] = [
  {
    memory_id: "glm_quality_output_preferences_v1",
    tenant_id: "owner_admin_internal",
    client_display_name: "Owner Admin Workspace",
    agent_key: "head_agent",
    source_scope: "quality_loop",
    sensitivity: "admin_only",
    memory_type: "quality_preference",
    summary:
      "Prefer outputs that include clear deliverables, evidence of action, and customer-safe wording before client presentation.",
    safe_client_summary: "Quality preferences applied.",
    learning_signal: "prioritise clear deliverables and client-safe presentation",
    quality_signal: "positive",
    owner_approved: true,
    client_visible: false,
    proprietary_logic_exposed: false,
    created_at: nowIso(),
    updated_at: nowIso(),
  },
  {
    memory_id: "glm_client_brand_adaptation_v1",
    tenant_id: "client_workspace_default",
    client_display_name: "Client Workspace",
    agent_key: "marketing_specialist_agent",
    source_scope: "client_workspace",
    sensitivity: "client_safe",
    memory_type: "brand_adaptation",
    summary:
      "Use saved business profile signals to adapt outputs to the client's offer, audience, positioning, brand voice, and region.",
    safe_client_summary: "Brand preferences and business profile details applied.",
    learning_signal: "adapt outputs using approved business profile context",
    quality_signal: "positive",
    owner_approved: true,
    client_visible: true,
    proprietary_logic_exposed: false,
    created_at: nowIso(),
    updated_at: nowIso(),
  },
  {
    memory_id: "glm_governance_boundary_v1",
    tenant_id: "platform_governance",
    client_display_name: "Platform Governance",
    agent_key: "orchestration_agent",
    source_scope: "agent_runtime",
    sensitivity: "proprietary_internal",
    memory_type: "governance_boundary",
    summary:
      "Learning memory may improve future recommendations and output formatting, but must not autonomously retrain models, expose prompts, expose routing logic, or alter spend/scaling strategy without owner approval.",
    safe_client_summary: "Governed quality checks passed.",
    learning_signal: "preserve governance boundaries and hide proprietary internal logic",
    quality_signal: "neutral",
    owner_approved: true,
    client_visible: false,
    proprietary_logic_exposed: false,
    created_at: nowIso(),
    updated_at: nowIso(),
  },
];

export function getGovernedLearningMemoryStatus(): GovernedLearningMemoryStatus {
  const records = baseRecords.map((record) => ({
    ...record,
    updated_at: nowIso(),
  }));

  const clientSafeRecords = records.filter(
    (record) =>
      record.client_visible === true &&
      record.sensitivity === "client_safe" &&
      record.proprietary_logic_exposed === false
  );

  return {
    success: true,
    row: 16,
    layer: "governed_learning_memory",
    status: "ready",
    governed_memory_enabled: true,
    client_safe_visibility: true,
    proprietary_logic_hidden_from_clients: true,
    owner_admin_diagnostics_enabled: true,
    no_autonomous_retraining: true,
    owner_approval_required_for_learning_policy_changes: true,
    tenant_isolation_enforced: true,
    memory_record_count: records.length,
    records,
    client_safe_records: clientSafeRecords,
  };
}

export function getClientSafeGovernedLearningMemoryStatus() {
  const status = getGovernedLearningMemoryStatus();

  return {
    success: status.success,
    row: status.row,
    layer: status.layer,
    status: status.status,
    governed_memory_enabled: status.governed_memory_enabled,
    client_safe_visibility: status.client_safe_visibility,
    proprietary_logic_hidden_from_clients:
      status.proprietary_logic_hidden_from_clients,
    no_autonomous_retraining: status.no_autonomous_retraining,
    memory_record_count: status.client_safe_records.length,
    records: status.client_safe_records.map((record) => ({
      memory_id: record.memory_id,
      client_display_name: record.client_display_name,
      agent_key: record.agent_key,
      memory_type: record.memory_type,
      safe_client_summary: record.safe_client_summary,
      quality_signal: record.quality_signal,
      client_visible: record.client_visible,
      proprietary_logic_exposed: record.proprietary_logic_exposed,
      updated_at: record.updated_at,
    })),
  };
}
