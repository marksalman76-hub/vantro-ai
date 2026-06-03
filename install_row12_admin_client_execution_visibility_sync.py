from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row12_admin_client_visibility_sync_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

sync_lib = ROOT / "frontend" / "src" / "lib" / "adminClientExecutionVisibilitySync.ts"
client_route = ROOT / "frontend" / "src" / "app" / "api" / "client-execution-visibility-sync" / "route.ts"
admin_route = ROOT / "frontend" / "src" / "app" / "api" / "admin-client-execution-visibility-sync" / "route.ts"
matrix_route = ROOT / "frontend" / "src" / "app" / "api" / "client-execution-matrix" / "route.ts"

for p in [sync_lib, client_route, admin_route, matrix_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

sync_lib.parent.mkdir(parents=True, exist_ok=True)

sync_lib.write_text(r'''import { getExecutionState } from "@/lib/executionStateSync";
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
''', encoding="utf-8")

client_route.parent.mkdir(parents=True, exist_ok=True)
client_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { buildAdminClientExecutionVisibilityPacket } from "@/lib/adminClientExecutionVisibilitySync";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});

  return NextResponse.json(
    buildAdminClientExecutionVisibilityPacket(tenantKey, "client"),
    {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    }
  );
}
''', encoding="utf-8")

admin_route.parent.mkdir(parents=True, exist_ok=True)
admin_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { buildAdminClientExecutionVisibilityPacket } from "@/lib/adminClientExecutionVisibilitySync";

export const dynamic = "force-dynamic";

function isAdminRequest(req: NextRequest): boolean {
  return Boolean(
    req.headers.get("authorization") ||
    req.headers.get("x-admin-token") ||
    req.cookies.get("admin_session")?.value
  );
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  if (!isAdminRequest(req)) {
    return NextResponse.json(
      { success: false, error: "Admin authorisation required." },
      { status: 401 }
    );
  }

  const tenantKey =
    req.nextUrl.searchParams.get("tenant_key") ||
    req.nextUrl.searchParams.get("tenant_id") ||
    req.headers.get("x-tenant-key") ||
    req.headers.get("x-tenant-id") ||
    "default_client_workspace";

  return NextResponse.json(
    buildAdminClientExecutionVisibilityPacket(tenantKey, "admin"),
    {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    }
  );
}
''', encoding="utf-8")

matrix_text = matrix_route.read_text(encoding="utf-8")

if 'adminClientExecutionVisibilitySync' not in matrix_text:
    matrix_text = matrix_text.replace(
        'import { getBusinessProfile } from "@/lib/businessProfilePersistence";',
        'import { getBusinessProfile } from "@/lib/businessProfilePersistence";\nimport { buildAdminClientExecutionVisibilityPacket } from "@/lib/adminClientExecutionVisibilitySync";'
    )

if "visibility_sync" not in matrix_text:
    matrix_text = matrix_text.replace(
        '''  return NextResponse.json({
    success: true,
    execution_state_synchronised: true,''',
        '''  const visibilitySync = buildAdminClientExecutionVisibilityPacket(tenantKey, "client");

  return NextResponse.json({
    success: true,
    execution_state_synchronised: true,
    admin_client_execution_visibility_sync_enabled: true,
    visibility_sync: visibilitySync,''',
    )

matrix_route.write_text(matrix_text, encoding="utf-8")

test = ROOT / "test_row12_admin_client_execution_visibility_sync.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/adminClientExecutionVisibilitySync.ts": [
        "buildAdminClientExecutionVisibilityPacket",
        "admin_client_execution_visibility_sync_enabled",
        "credential_values_exposed: false",
        "owner_visibility",
        "synced_sections",
    ],
    "frontend/src/app/api/client-execution-visibility-sync/route.ts": [
        "buildAdminClientExecutionVisibilityPacket",
        "client",
        "cache-control",
    ],
    "frontend/src/app/api/admin-client-execution-visibility-sync/route.ts": [
        "Admin authorisation required",
        "buildAdminClientExecutionVisibilityPacket",
        "admin",
        "tenant_key",
    ],
    "frontend/src/app/api/client-execution-matrix/route.ts": [
        "admin_client_execution_visibility_sync_enabled",
        "visibility_sync",
        "buildAdminClientExecutionVisibilityPacket",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW12_ADMIN_CLIENT_EXECUTION_VISIBILITY_SYNC_FAILED missing={missing}")

print("ROW12_ADMIN_CLIENT_EXECUTION_VISIBILITY_SYNC_PASSED")
''', encoding="utf-8")

print("ROW12_ADMIN_CLIENT_EXECUTION_VISIBILITY_SYNC_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {sync_lib}")
print(f"Created/updated: {client_route}")
print(f"Created/updated: {admin_route}")
print(f"Updated: {matrix_route}")
print(f"Created: {test}")