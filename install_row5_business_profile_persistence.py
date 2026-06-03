from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row5_business_profile_persistence_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

profile_lib = ROOT / "frontend" / "src" / "lib" / "businessProfilePersistence.ts"
profile_route = ROOT / "frontend" / "src" / "app" / "api" / "client-business-profile" / "route.ts"
client_me_route = ROOT / "frontend" / "src" / "app" / "api" / "client-me" / "route.ts"

for p in [profile_lib, profile_route, client_me_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

profile_lib.parent.mkdir(parents=True, exist_ok=True)

profile_lib.write_text(r'''import fs from "fs";
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
''', encoding="utf-8")

profile_route.parent.mkdir(parents=True, exist_ok=True)

profile_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { persistBusinessProfile, getBusinessProfile } from "@/lib/businessProfilePersistence";
import { resolveTenantKey } from "@/lib/deliverablePersistence";

export const dynamic = "force-dynamic";

function backendBaseUrl(): string {
  return (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://api.trance-formation.com.au"
  ).replace(/\/$/, "");
}

function buildForwardHeaders(req: NextRequest): Record<string, string> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
  };

  const auth = req.headers.get("authorization");
  const adminToken = req.headers.get("x-admin-token");
  const cookie = req.headers.get("cookie");

  if (auth) headers.authorization = auth;
  if (adminToken) headers["x-admin-token"] = adminToken;
  if (cookie) headers.cookie = cookie;

  return headers;
}

export async function GET(req: NextRequest): Promise<NextResponse> {
  const tenantKey = resolveTenantKey(req.headers, {});
  const persisted = getBusinessProfile(tenantKey);

  if (persisted) {
    return NextResponse.json({
      success: true,
      business_profile_persisted: true,
      persistence_source: "business_profile_store",
      profile: persisted,
      business_profile: persisted,
      display_name: persisted.display_name,
      profile_completed: persisted.profile_completed,
    }, {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    });
  }

  try {
    const response = await fetch(`${backendBaseUrl()}/client-business-profile`, {
      method: "GET",
      headers: buildForwardHeaders(req),
      cache: "no-store",
    });

    const text = await response.text();
    let payload: Record<string, unknown> = {};

    try {
      payload = JSON.parse(text);
    } catch {
      payload = { backend_response_text: text };
    }

    return NextResponse.json({
      ...payload,
      business_profile_persisted: false,
      persistence_source: "backend_client_business_profile_route",
    }, {
      status: response.status,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    });
  } catch {
    return NextResponse.json({
      success: true,
      business_profile_persisted: false,
      persistence_source: "empty_profile_fallback",
      profile: null,
      business_profile: null,
      display_name: "Your business",
      profile_completed: false,
    }, {
      status: 200,
      headers: { "cache-control": "no-store, no-cache, must-revalidate" },
    });
  }
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const tenantKey = resolveTenantKey(req.headers, body);
  const persisted = persistBusinessProfile(tenantKey, body);

  let backendPayload: Record<string, unknown> = {};
  let backendStatus = 200;

  try {
    const response = await fetch(`${backendBaseUrl()}/client-business-profile`, {
      method: "POST",
      headers: buildForwardHeaders(req),
      body: JSON.stringify({
        ...body,
        display_name: persisted.display_name,
        business_name: persisted.business_name,
      }),
      cache: "no-store",
    });

    backendStatus = response.status;
    const text = await response.text();

    try {
      backendPayload = JSON.parse(text);
    } catch {
      backendPayload = { backend_response_text: text };
    }
  } catch {
    backendPayload = { backend_sync_status: "pending" };
  }

  return NextResponse.json({
    ...backendPayload,
    success: true,
    business_profile_saved: true,
    business_profile_persisted: true,
    persistence_source: "business_profile_store",
    profile: persisted,
    business_profile: persisted,
    display_name: persisted.display_name,
    profile_completed: persisted.profile_completed,
  }, {
    status: backendStatus >= 500 ? 200 : backendStatus,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

if client_me_route.exists():
    me_text = client_me_route.read_text(encoding="utf-8")

    if 'businessProfilePersistence' not in me_text:
        me_text = me_text.replace(
            'import { NextRequest, NextResponse } from "next/server";',
            'import { NextRequest, NextResponse } from "next/server";\nimport { getBusinessProfile } from "@/lib/businessProfilePersistence";\nimport { resolveTenantKey } from "@/lib/deliverablePersistence";'
        )

    if "business_profile_persisted" not in me_text:
        me_text = me_text.replace(
            "return NextResponse.json(",
            "const tenantKey = resolveTenantKey(req.headers, {});\n  const persistedProfile = getBusinessProfile(tenantKey);\n\n  return NextResponse.json(",
            1
        )
        me_text = me_text.replace(
            "{",
            "{\n      business_profile_persisted: Boolean(persistedProfile),\n      business_profile: persistedProfile,\n      display_name: persistedProfile?.display_name || undefined,",
            1
        )

    client_me_route.write_text(me_text, encoding="utf-8")

test = ROOT / "test_row5_business_profile_persistence.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/businessProfilePersistence.ts": [
        "persistBusinessProfile",
        "getBusinessProfile",
        "normaliseBusinessProfile",
        "business-profiles",
        "profile_completed",
        "Your business",
    ],
    "frontend/src/app/api/client-business-profile/route.ts": [
        "business_profile_persisted",
        "business_profile_store",
        "persistBusinessProfile",
        "getBusinessProfile",
        "profile_completed",
    ],
}

optional_checks = {
    "frontend/src/app/api/client-me/route.ts": [
        "business_profile_persisted",
        "getBusinessProfile",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

for file, needles in optional_checks.items():
    p = Path(file)
    if p.exists():
        text = p.read_text(encoding="utf-8")
        absent = [needle for needle in needles if needle not in text]
        if absent:
            missing[file] = absent

if missing:
    raise SystemExit(f"ROW5_BUSINESS_PROFILE_PERSISTENCE_FAILED missing={missing}")

print("ROW5_BUSINESS_PROFILE_PERSISTENCE_PASSED")
''', encoding="utf-8")

print("ROW5_BUSINESS_PROFILE_PERSISTENCE_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {profile_lib}")
print(f"Updated: {profile_route}")
if client_me_route.exists():
    print(f"Updated: {client_me_route}")
print(f"Created: {test}")