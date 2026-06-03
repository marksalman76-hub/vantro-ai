import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { getMediaAssets, getLatestMediaAsset } from "@/lib/mediaAssetLifecycle";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const assets = getMediaAssets(tenantKey);
  const latest = getLatestMediaAsset(tenantKey);

  return NextResponse.json({
    success: true,
    tenant_scoped: true,
    client_safe: true,
    media_asset_lifecycle_enabled: true,
    asset_count: assets.length,
    media_assets: assets,
    latest_media_asset: latest,
    asset_preview_ready: Boolean(latest?.preview_ready),
    asset_download_ready: Boolean(latest?.download_ready),
    asset_lifecycle_status: latest?.lifecycle_status || "unavailable",
  }, {
    status: 200,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}
