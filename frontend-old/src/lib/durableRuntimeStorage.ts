import fs from "fs";
import path from "path";

export type DurableRuntimeStoreHealth = {
  store_key: string;
  path: string;
  exists: boolean;
  readable: boolean;
  writable: boolean;
  size_bytes: number;
  last_modified_at: string | null;
};

export type DurableRuntimeStorageStatus = {
  success: true;
  durable_runtime_storage_enabled: true;
  storage_root: string;
  store_count: number;
  healthy_store_count: number;
  stores: DurableRuntimeStoreHealth[];
  client_safe: true;
  credential_values_exposed: false;
};

export const DURABLE_RUNTIME_STORAGE_ROOT = path.join(process.cwd(), ".runtime");

export const DURABLE_RUNTIME_STORE_PATHS: Record<string, string> = {
  client_deliverables: path.join(DURABLE_RUNTIME_STORAGE_ROOT, "client-deliverables", "latest-deliverables.json"),
  approval_history: path.join(DURABLE_RUNTIME_STORAGE_ROOT, "approval-history", "approval-revision-history.json"),
  business_profiles: path.join(DURABLE_RUNTIME_STORAGE_ROOT, "business-profiles", "business-profiles.json"),
  execution_state: path.join(DURABLE_RUNTIME_STORAGE_ROOT, "execution-state", "client-execution-state.json"),
  media_assets: path.join(DURABLE_RUNTIME_STORAGE_ROOT, "media-assets", "media-assets.json"),
  provider_queue: path.join(DURABLE_RUNTIME_STORAGE_ROOT, "provider-queue", "provider-queue.json"),
  billing_subscriptions: path.join(DURABLE_RUNTIME_STORAGE_ROOT, "billing-subscriptions", "billing-subscriptions.json"),
  credit_ledger: path.join(DURABLE_RUNTIME_STORAGE_ROOT, "package-credit-enforcement", "credit-ledger.json"),
};

export function ensureDurableRuntimeStorage(): void {
  fs.mkdirSync(DURABLE_RUNTIME_STORAGE_ROOT, { recursive: true });

  for (const filePath of Object.values(DURABLE_RUNTIME_STORE_PATHS)) {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });

    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, JSON.stringify({}, null, 2), "utf-8");
    }
  }
}

export function durableReadJson<T>(filePath: string, fallback: T): T {
  ensureDurableRuntimeStorage();

  try {
    if (!fs.existsSync(filePath)) return fallback;

    const parsed = JSON.parse(fs.readFileSync(filePath, "utf-8"));

    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return fallback;
    }

    return parsed as T;
  } catch {
    return fallback;
  }
}

export function durableWriteJson<T>(filePath: string, value: T): void {
  ensureDurableRuntimeStorage();

  fs.mkdirSync(path.dirname(filePath), { recursive: true });

  const tmp = `${filePath}.tmp`;

  fs.writeFileSync(tmp, JSON.stringify(value, null, 2), "utf-8");
  fs.renameSync(tmp, filePath);
}

export function inspectDurableRuntimeStore(storeKey: string, filePath: string): DurableRuntimeStoreHealth {
  let exists = false;
  let readable = false;
  let writable = false;
  let sizeBytes = 0;
  let lastModifiedAt: string | null = null;

  try {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    exists = fs.existsSync(filePath);

    if (!exists) {
      fs.writeFileSync(filePath, JSON.stringify({}, null, 2), "utf-8");
      exists = true;
    }

    const stat = fs.statSync(filePath);
    sizeBytes = stat.size;
    lastModifiedAt = stat.mtime.toISOString();

    fs.readFileSync(filePath, "utf-8");
    readable = true;

    const probe = `${filePath}.probe`;
    fs.writeFileSync(probe, "ok", "utf-8");
    fs.unlinkSync(probe);
    writable = true;
  } catch {
    // Health flags remain false where relevant.
  }

  return {
    store_key: storeKey,
    path: filePath,
    exists,
    readable,
    writable,
    size_bytes: sizeBytes,
    last_modified_at: lastModifiedAt,
  };
}

export function buildDurableRuntimeStorageStatus(): DurableRuntimeStorageStatus {
  ensureDurableRuntimeStorage();

  const stores = Object.entries(DURABLE_RUNTIME_STORE_PATHS).map(([storeKey, filePath]) =>
    inspectDurableRuntimeStore(storeKey, filePath)
  );

  const healthyStoreCount = stores.filter(
    (store) => store.exists && store.readable && store.writable
  ).length;

  return {
    success: true,
    durable_runtime_storage_enabled: true,
    storage_root: DURABLE_RUNTIME_STORAGE_ROOT,
    store_count: stores.length,
    healthy_store_count: healthyStoreCount,
    stores,
    client_safe: true,
    credential_values_exposed: false,
  };
}
