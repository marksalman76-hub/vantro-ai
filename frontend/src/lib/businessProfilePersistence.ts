import fs from "fs";
import path from "path";

export type BusinessProfileRecord = {
  tenant_key: string;
  updated_at: string;
  business_name: string;
  display_name: string;
  industry: string;
  business_type: string;
  target_audience: string;
  location: string;
  website: string;
  brand_voice: string;
  primary_goal: string;
  offer_summary: string;
  notes: string;
  profile_completed: boolean;
};

const STORE_DIR = path.join(process.cwd(), ".runtime", "business-profiles");
const STORE_FILE = path.join(STORE_DIR, "business-profiles.json");

function ensureStore(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });
  if (!fs.existsSync(STORE_FILE)) {
    fs.writeFileSync(STORE_FILE, JSON.stringify({ profiles: {} }, null, 2), "utf-8");
  }
}

function safeReadStore(): { profiles: Record<string, BusinessProfileRecord> } {
  ensureStore();

  try {
    const parsed = JSON.parse(fs.readFileSync(STORE_FILE, "utf-8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return { profiles: {} };
    if (!parsed.profiles || typeof parsed.profiles !== "object" || Array.isArray(parsed.profiles)) return { profiles: {} };
    return parsed as { profiles: Record<string, BusinessProfileRecord> };
  } catch {
    return { profiles: {} };
  }
}

function safeWriteStore(store: { profiles: Record<string, BusinessProfileRecord> }): void {
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

function cleanDisplayName(value: unknown): string {
  const raw = text(value);
  if (!raw) return "";
  if (/^client[_-]/i.test(raw)) return "";
  if (/^tenant[_-]/i.test(raw)) return "";
  return raw;
}

export function normaliseBusinessProfile(
  tenantKey: string,
  payload: Record<string, unknown>
): BusinessProfileRecord {
  const businessName = cleanDisplayName(
    payload.business_name ||
    payload.businessName ||
    payload.company_name ||
    payload.companyName ||
    payload.display_name ||
    payload.displayName
  );

  const displayName = businessName || cleanDisplayName(payload.name) || "Your business";

  const record: BusinessProfileRecord = {
    tenant_key: tenantKey,
    updated_at: new Date().toISOString(),
    business_name: businessName || displayName,
    display_name: displayName,
    industry: text(payload.industry),
    business_type: text(payload.business_type || payload.businessType),
    target_audience: text(payload.target_audience || payload.targetAudience),
    location: text(payload.location),
    website: text(payload.website),
    brand_voice: text(payload.brand_voice || payload.brandVoice),
    primary_goal: text(payload.primary_goal || payload.primaryGoal),
    offer_summary: text(payload.offer_summary || payload.offerSummary),
    notes: text(payload.notes),
    profile_completed: Boolean(
      businessName &&
      (
        text(payload.industry) ||
        text(payload.business_type || payload.businessType) ||
        text(payload.target_audience || payload.targetAudience) ||
        text(payload.primary_goal || payload.primaryGoal)
      )
    ),
  };

  return record;
}

export function persistBusinessProfile(
  tenantKey: string,
  payload: Record<string, unknown>
): BusinessProfileRecord {
  const record = normaliseBusinessProfile(tenantKey, payload);
  const store = safeReadStore();
  store.profiles[tenantKey] = record;
  safeWriteStore(store);
  return record;
}

export function getBusinessProfile(tenantKey: string): BusinessProfileRecord | null {
  const store = safeReadStore();
  return store.profiles[tenantKey] || null;
}
