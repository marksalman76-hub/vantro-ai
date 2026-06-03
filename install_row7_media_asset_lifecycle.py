from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row7_media_asset_lifecycle_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

asset_lib = ROOT / "frontend" / "src" / "lib" / "mediaAssetLifecycle.ts"
delegated_route = ROOT / "frontend" / "src" / "app" / "api" / "delegated-workforce-execution" / "route.ts"
latest_route = ROOT / "frontend" / "src" / "app" / "api" / "client-latest-deliverable" / "route.ts"
assets_route = ROOT / "frontend" / "src" / "app" / "api" / "client-media-assets" / "route.ts"

for p in [asset_lib, delegated_route, latest_route, assets_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

asset_lib.parent.mkdir(parents=True, exist_ok=True)

asset_lib.write_text(r'''import fs from "fs";
import path from "path";

export type MediaAssetRecord = {
  id: string;
  tenant_key: string;
  created_at: string;
  updated_at: string;
  source: string;
  asset_type: string;
  lifecycle_status: "preview_ready" | "download_ready" | "pending" | "expired" | "unavailable";
  preview_ready: boolean;
  download_ready: boolean;
  preview_url: string;
  download_url: string;
  public_url: string;
  signed_preview_url: string;
  signed_download_url: string;
  expires_at: string | null;
  client_safe: boolean;
  metadata: Record<string, unknown>;
};

const STORE_DIR = path.join(process.cwd(), ".runtime", "media-assets");
const STORE_FILE = path.join(STORE_DIR, "media-assets.json");

function ensureStore(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });
  if (!fs.existsSync(STORE_FILE)) {
    fs.writeFileSync(STORE_FILE, JSON.stringify({ assets: {} }, null, 2), "utf-8");
  }
}

function safeReadStore(): { assets: Record<string, MediaAssetRecord[]> } {
  ensureStore();

  try {
    const parsed = JSON.parse(fs.readFileSync(STORE_FILE, "utf-8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return { assets: {} };
    if (!parsed.assets || typeof parsed.assets !== "object" || Array.isArray(parsed.assets)) return { assets: {} };
    return parsed as { assets: Record<string, MediaAssetRecord[]> };
  } catch {
    return { assets: {} };
  }
}

function safeWriteStore(store: { assets: Record<string, MediaAssetRecord[]> }): void {
  ensureStore();
  const tmp = `${STORE_FILE}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(store, null, 2), "utf-8");
  fs.renameSync(tmp, STORE_FILE);
}

function text(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return "";
}

function objectValue(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  return value as Record<string, unknown>;
}

function futureExpiry(): string {
  const date = new Date();
  date.setDate(date.getDate() + 30);
  return date.toISOString();
}

function resolveLifecycleStatus(asset: Record<string, unknown>): MediaAssetRecord["lifecycle_status"] {
  const previewUrl = text(asset.preview_url || asset.signed_preview_url || asset.public_url || asset.url);
  const downloadUrl = text(asset.download_url || asset.signed_download_url);

  if (downloadUrl) return "download_ready";
  if (previewUrl) return "preview_ready";
  if (asset.preview_ready === true) return "preview_ready";
  if (asset.download_ready === true) return "download_ready";
  if (asset.expired === true) return "expired";
  return "pending";
}

export function extractMediaAssetCandidates(payload: Record<string, unknown>): Record<string, unknown>[] {
  const result = objectValue(payload.result);
  const data = objectValue(payload.data);

  const rawCandidates: unknown[] = [
    payload.asset,
    payload.assets,
    result.asset,
    result.assets,
    data.asset,
    data.assets,
    payload.media_asset,
    payload.media_assets,
    result.media_asset,
    result.media_assets,
    data.media_asset,
    data.media_assets,
  ];

  const flattened: Record<string, unknown>[] = [];

  for (const candidate of rawCandidates) {
    if (Array.isArray(candidate)) {
      for (const item of candidate) {
        const obj = objectValue(item);
        if (Object.keys(obj).length) flattened.push(obj);
      }
    } else {
      const obj = objectValue(candidate);
      if (Object.keys(obj).length) flattened.push(obj);
    }
  }

  return flattened;
}

export function persistMediaAssets(
  tenantKey: string,
  payload: Record<string, unknown>,
  source = "delegated_workforce_execution"
): MediaAssetRecord[] {
  const candidates = extractMediaAssetCandidates(payload);
  if (!candidates.length) return [];

  const now = new Date().toISOString();

  const records = candidates.map((asset, index): MediaAssetRecord => {
    const lifecycleStatus = resolveLifecycleStatus(asset);
    const previewUrl = text(asset.preview_url || asset.url || asset.public_url);
    const downloadUrl = text(asset.download_url);
    const signedPreviewUrl = text(asset.signed_preview_url);
    const signedDownloadUrl = text(asset.signed_download_url);

    return {
      id: text(asset.id || asset.asset_id) || `${tenantKey}_asset_${Date.now()}_${index}`,
      tenant_key: tenantKey,
      created_at: text(asset.created_at) || now,
      updated_at: now,
      source,
      asset_type: text(asset.asset_type || asset.type || asset.mime_type) || "generated_asset",
      lifecycle_status: lifecycleStatus,
      preview_ready: lifecycleStatus === "preview_ready" || lifecycleStatus === "download_ready",
      download_ready: lifecycleStatus === "download_ready",
      preview_url: previewUrl,
      download_url: downloadUrl,
      public_url: text(asset.public_url || asset.url),
      signed_preview_url: signedPreviewUrl,
      signed_download_url: signedDownloadUrl,
      expires_at: text(asset.expires_at) || futureExpiry(),
      client_safe: true,
      metadata: {
        provider: text(asset.provider),
        filename: text(asset.filename),
        size_bytes: asset.size_bytes || null,
        original_status: text(asset.status),
      },
    };
  });

  const store = safeReadStore();
  const existing = store.assets[tenantKey] || [];
  const merged = [...records, ...existing];

  const deduped: MediaAssetRecord[] = [];
  const seen = new Set<string>();

  for (const record of merged) {
    if (seen.has(record.id)) continue;
    seen.add(record.id);
    deduped.push(record);
  }

  store.assets[tenantKey] = deduped.slice(0, 100);
  safeWriteStore(store);

  return records;
}

export function getMediaAssets(tenantKey: string): MediaAssetRecord[] {
  const store = safeReadStore();
  const assets = store.assets[tenantKey] || [];
  const now = Date.now();

  return assets.map((asset) => {
    if (asset.expires_at && Date.parse(asset.expires_at) < now) {
      return {
        ...asset,
        lifecycle_status: "expired",
        preview_ready: false,
        download_ready: false,
      };
    }

    return asset;
  });
}

export function getLatestMediaAsset(tenantKey: string): MediaAssetRecord | null {
  return getMediaAssets(tenantKey)[0] || null;
}

export function attachMediaAssetLifecycle(
  tenantKey: string,
  payload: Record<string, unknown>
): Record<string, unknown> {
  const assets = getMediaAssets(tenantKey);
  const latest = assets[0] || null;

  return {
    ...payload,
    media_asset_lifecycle_enabled: true,
    media_assets: assets,
    latest_media_asset: latest,
    asset_preview_ready: Boolean(latest?.preview_ready),
    asset_download_ready: Boolean(latest?.download_ready),
    asset_lifecycle_status: latest?.lifecycle_status || "unavailable",
  };
}
''', encoding="utf-8")

# Patch delegated route
delegated_text = delegated_route.read_text(encoding="utf-8")

if 'mediaAssetLifecycle' not in delegated_text:
    delegated_text = delegated_text.replace(
        'import { persistExecutionState } from "@/lib/executionStateSync";',
        'import { persistExecutionState } from "@/lib/executionStateSync";\nimport { persistMediaAssets, attachMediaAssetLifecycle } from "@/lib/mediaAssetLifecycle";'
    )

delegated_text = delegated_text.replace(
    '''  const stateTenantKey = resolveTenantKey(req.headers, normalised);
  const executionState = persistExecutionState(stateTenantKey, normalised);
  normalised.execution_state_synchronised = true;
  normalised.execution_state = executionState;''',
    '''  const stateTenantKey = resolveTenantKey(req.headers, normalised);
  const persistedMediaAssets = persistMediaAssets(stateTenantKey, normalised, "delegated_workforce_execution");
  normalised.media_asset_lifecycle_enabled = true;
  normalised.media_assets_persisted = persistedMediaAssets.length;
  const lifecyclePayload = attachMediaAssetLifecycle(stateTenantKey, normalised);
  Object.assign(normalised, lifecyclePayload);
  const executionState = persistExecutionState(stateTenantKey, normalised);
  normalised.execution_state_synchronised = true;
  normalised.execution_state = executionState;'''
)

delegated_route.write_text(delegated_text, encoding="utf-8")

# Patch latest route
latest_text = latest_route.read_text(encoding="utf-8")

if 'mediaAssetLifecycle' not in latest_text:
    latest_text = latest_text.replace(
        'import { mergeExecutionState, persistExecutionState } from "@/lib/executionStateSync";',
        'import { mergeExecutionState, persistExecutionState } from "@/lib/executionStateSync";\nimport { attachMediaAssetLifecycle } from "@/lib/mediaAssetLifecycle";'
    )

latest_text = latest_text.replace(
    '''      return NextResponse.json({
        ...persistedPayload,
        execution_state_synchronised: true,
        execution_state: syncedState,
      }, {''',
    '''      return NextResponse.json(attachMediaAssetLifecycle(tenantKey, {
        ...persistedPayload,
        execution_state_synchronised: true,
        execution_state: syncedState,
      }), {'''
)

latest_text = latest_text.replace(
    '''  return NextResponse.json(latestPayload, {''',
    '''  return NextResponse.json(attachMediaAssetLifecycle(tenantKey, latestPayload), {'''
)

latest_route.write_text(latest_text, encoding="utf-8")

# Create client media assets route
assets_route.parent.mkdir(parents=True, exist_ok=True)

assets_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
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
''', encoding="utf-8")

test = ROOT / "test_row7_media_asset_lifecycle.py"

test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/mediaAssetLifecycle.ts": [
        "persistMediaAssets",
        "getMediaAssets",
        "getLatestMediaAsset",
        "attachMediaAssetLifecycle",
        "media-assets.json",
        "preview_ready",
        "download_ready",
        "expired",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "persistMediaAssets",
        "attachMediaAssetLifecycle",
        "media_assets_persisted",
        "media_asset_lifecycle_enabled",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "attachMediaAssetLifecycle",
        "media_asset_lifecycle_enabled",
    ],
    "frontend/src/app/api/client-media-assets/route.ts": [
        "getMediaAssets",
        "getLatestMediaAsset",
        "asset_lifecycle_status",
        "asset_preview_ready",
        "asset_download_ready",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW7_MEDIA_ASSET_LIFECYCLE_FAILED missing={missing}")

print("ROW7_MEDIA_ASSET_LIFECYCLE_PASSED")
''', encoding="utf-8")

print("ROW7_MEDIA_ASSET_LIFECYCLE_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {asset_lib}")
print(f"Updated: {delegated_route}")
print(f"Updated: {latest_route}")
print(f"Created/updated: {assets_route}")
print(f"Created: {test}")