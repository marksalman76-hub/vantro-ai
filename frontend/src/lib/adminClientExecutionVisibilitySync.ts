import { getExecutionState } from "@/lib/executionStateSync";
import { getLatestDeliverable } from "@/lib/deliverablePersistence";
import { getApprovalRevisionHistory } from "@/lib/approvalRevisionHistory";
import { getBusinessProfile } from "@/lib/businessProfilePersistence";
import { getMediaAssets, getLatestMediaAsset } from "@/lib/mediaAssetLifecycle";
import { getLatestProviderQueueJob, getProviderQueueJobs } from "@/lib/providerQueueRetryFailover";

export type VisibilityMode = "client" | "admin";

export function buildAdminClientExecutionVisibilityPacket(
  tenantKey: string,
  mode: VisibilityMode = "client"
): Record<string, unknown> {
  const executionState = getExecutionState(tenantKey);
  const latestDeliverable = getLatestDeliverable(tenantKey);
  const approvalHistory = getApprovalRevisionHistory(tenantKey);
  const businessProfile = getBusinessProfile(tenantKey);
  const mediaAssets = getMediaAssets(tenantKey);
  const latestMediaAsset = getLatestMediaAsset(tenantKey);
  const providerQueueJobs = getProviderQueueJobs(tenantKey);
  const latestProviderQueueJob = getLatestProviderQueueJob(tenantKey);

  const hasRealOutput = Boolean(
    executionState?.has_real_output ||
    latestDeliverable?.has_real_output
  );

  const packet = {
    success: true,
    admin_client_execution_visibility_sync_enabled: true,
    visibility_mode: mode,
    tenant_scoped: true,
    client_safe: true,
    credential_values_exposed: false,
    execution_state: executionState,
    latest_deliverable: latestDeliverable,
    latest_review_action: approvalHistory[0] || null,
    approval_revision_history: approvalHistory,
    business_profile: businessProfile,
    media_assets: mediaAssets,
    latest_media_asset: latestMediaAsset,
    provider_queue_jobs: mode === "admin" ? providerQueueJobs : providerQueueJobs.slice(0, 5),
    latest_provider_queue_job: latestProviderQueueJob,
    has_real_output: hasRealOutput,
    display_status:
      executionState?.display_status ||
      latestDeliverable?.display_status ||
      (hasRealOutput ? "Completed" : "Output pending"),
    client_safe_status:
      executionState?.client_safe_status ||
      latestDeliverable?.client_safe_status ||
      (hasRealOutput ? "Completed" : "Output pending"),
    synced_sections: {
      execution_state: Boolean(executionState),
      latest_deliverable: Boolean(latestDeliverable),
      approval_revision_history: approvalHistory.length > 0,
      business_profile: Boolean(businessProfile),
      media_assets: mediaAssets.length > 0,
      provider_queue: providerQueueJobs.length > 0,
    },
  };

  if (mode === "admin") {
    return {
      ...packet,
      admin_safe: true,
      owner_visibility: true,
      client_restricted: false,
      admin_notes:
        "Owner/admin visibility is unrestricted for monitoring, while credential values remain hidden.",
    };
  }

  return packet;
}
