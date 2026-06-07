import { NextRequest, NextResponse } from "next/server";
import { resolveTenantKey } from "@/lib/deliverablePersistence";
import { getMediaAssets, getLatestMediaAsset } from "@/lib/mediaAssetLifecycle";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.BACKEND_BASE_URL ||
    process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function isProduction(): boolean {
  const value = String(process.env.NODE_ENV || process.env.VERCEL_ENV || process.env.ENVIRONMENT || "").toLowerCase();
  return value === "production" || value === "prod";
}

function advisoryPayload(tenantKey: string, status = 200): NextResponse {
  const assets = getMediaAssets(tenantKey);
  const latest = getLatestMediaAsset(tenantKey);

  return NextResponse.json({
    success: true,
    tenant_scoped: true,
    client_safe: true,
    authority: "frontend_advisory",
    fallback_used: true,
    dev_only: true,
    production_fail_closed: false,
    media_asset_lifecycle_enabled: true,
    asset_count: assets.length,
    media_assets: assets,
    latest_media_asset: latest,
    asset_preview_ready: Boolean(latest?.preview_ready),
    asset_download_ready: Boolean(latest?.download_ready),
    asset_lifecycle_status: latest?.lifecycle_status || "unavailable",
    credential_values_exposed: false,
  }, {
    status,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

function productionFailClosed(error: unknown): NextResponse {
  return NextResponse.json({
    success: false,
    tenant_scoped: true,
    client_safe: true,
    authority: "backend_canonical",
    fallback_used: false,
    dev_only: false,
    production_fail_closed: true,
    status: "canonical_media_metadata_unavailable",
    error: error instanceof Error ? error.message : String(error || "backend_unavailable"),
    media_asset_lifecycle_enabled: true,
    asset_count: 0,
    media_assets: [],
    latest_media_asset: null,
    asset_preview_ready: false,
    asset_download_ready: false,
    asset_lifecycle_status: "unavailable",
    credential_values_exposed: false,
  }, {
    status: 503,
    headers: {
      "cache-control": "no-store, no-cache, must-revalidate",
    },
  });
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const headers: Record<string, string> = {
    "cache-control": "no-store",
    "x-tenant-id": tenantKey,
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;

  try {
    const response = await fetch(`${backendBaseUrl()}/media/assets`, {
      method: "GET",
      cache: "no-store",
      headers,
    });
    const data = await response.json();

    if (response.ok && data && data.success !== false) {
      const assets = Array.isArray(data.assets) ? data.assets : [];
      const latest = assets[0] || null;
      return NextResponse.json({
        ...data,
        success: true,
        tenant_scoped: true,
        client_safe: true,
        authority: "backend_canonical",
        fallback_used: Boolean(data.fallback_used),
        dev_only: Boolean(data.dev_only),
        production_fail_closed: false,
        media_asset_lifecycle_enabled: true,
        asset_count: Number(data.asset_count ?? assets.length),
        media_assets: assets,
        latest_media_asset: latest,
        asset_preview_ready: Boolean(latest?.preview_ready),
        asset_download_ready: Boolean(latest?.download_ready),
        asset_lifecycle_status: latest ? (latest.lifecycle_status || latest.status || "preview_ready") : "unavailable",
        credential_values_exposed: false,
      }, {
        status: response.status,
        headers: {
          "cache-control": "no-store, no-cache, must-revalidate",
        },
      });
    }

    if (isProduction()) {
      return productionFailClosed(data?.detail || data?.error || data?.status || "backend_canonical_unavailable");
    }

    return advisoryPayload(tenantKey);
  } catch (error) {
    if (isProduction()) {
      return productionFailClosed(error);
    }

    return advisoryPayload(tenantKey);
  }
}
