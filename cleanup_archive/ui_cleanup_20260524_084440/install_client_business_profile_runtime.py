from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME = ROOT / "backend" / "app" / "core" / "client_business_profile_runtime.py"
FRONTEND_API_DIR = ROOT / "frontend" / "src" / "app" / "api" / "client-business-profile"
FRONTEND_API = FRONTEND_API_DIR / "route.ts"

for file in [MAIN]:
    backup = BACKUP_DIR / f"{file.stem}_before_client_business_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file.suffix}"
    backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

if FRONTEND_API.exists():
    backup = BACKUP_DIR / f"client_business_profile_route_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ts"
    backup.write_text(FRONTEND_API.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.core.postgres_account_runtime import get_connection, get_session_account


PROFILE_FIELDS = [
    "business_niche",
    "products_services",
    "target_audience",
    "competitors",
    "offers",
    "brand_voice",
    "goals",
    "region",
    "currency",
    "notes",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_profile(payload: Dict[str, Any]) -> Dict[str, str]:
    profile: Dict[str, str] = {}
    for field in PROFILE_FIELDS:
        value = payload.get(field)
        profile[field] = str(value or "").strip()[:4000]
    return profile


def ensure_client_business_profile_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS client_business_profiles (
                tenant_id TEXT PRIMARY KEY,
                profile_json TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            )
            """)
        conn.commit()


def get_client_business_profile(session_token: str) -> Dict[str, Any]:
    session = get_session_account(session_token)

    if not session.get("success"):
        return {"success": False, "error": session.get("error") or "invalid_session"}

    account = session.get("account") or {}
    tenant_id = str(account.get("tenant_id") or "").strip()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    ensure_client_business_profile_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT profile_json, created_at, updated_at
            FROM client_business_profiles
            WHERE tenant_id = %s
            """, (tenant_id,))
            row = cur.fetchone()

    if not row:
        return {
            "success": True,
            "tenant_id": tenant_id,
            "account": account,
            "profile": {field: "" for field in PROFILE_FIELDS},
            "profile_saved": False,
        }

    try:
        profile = json.loads(row[0] or "{}")
    except Exception:
        profile = {}

    profile = {field: str(profile.get(field) or "") for field in PROFILE_FIELDS}

    return {
        "success": True,
        "tenant_id": tenant_id,
        "account": account,
        "profile": profile,
        "profile_saved": True,
        "created_at": row[1].isoformat() if row[1] else None,
        "updated_at": row[2].isoformat() if row[2] else None,
    }


def save_client_business_profile(session_token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    session = get_session_account(session_token)

    if not session.get("success"):
        return {"success": False, "error": session.get("error") or "invalid_session"}

    account = session.get("account") or {}
    tenant_id = str(account.get("tenant_id") or "").strip()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    profile = _normalise_profile(payload)
    ensure_client_business_profile_table()

    now = _now_iso()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client_business_profiles (
                tenant_id,
                profile_json,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tenant_id)
            DO UPDATE SET
                profile_json = EXCLUDED.profile_json,
                updated_at = EXCLUDED.updated_at
            RETURNING tenant_id, profile_json, created_at, updated_at
            """, (
                tenant_id,
                json.dumps(profile),
                now,
                now,
            ))
            row = cur.fetchone()
        conn.commit()

    return {
        "success": True,
        "tenant_id": row[0],
        "account": account,
        "profile": json.loads(row[1] or "{}"),
        "profile_saved": True,
        "created_at": row[2].isoformat() if row[2] else None,
        "updated_at": row[3].isoformat() if row[3] else None,
        "customer_safe_response_mode": True,
    }
''', encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_line = "from backend.app.core.client_business_profile_runtime import get_client_business_profile, save_client_business_profile\n"
if import_line not in main_text:
    marker = "from backend.app.core.client_integrations_runtime import"
    if marker in main_text:
        main_text = main_text.replace(marker, import_line + marker, 1)
    else:
        main_text = import_line + main_text

routes_block = r'''

# Client business profile persistence runtime
@app.get("/client/business-profile")
async def client_business_profile_get(session_token: str):
    return get_client_business_profile(session_token)


@app.post("/client/business-profile")
async def client_business_profile_save(payload: dict):
    session_token = str(payload.get("session_token") or "")
    profile = payload.get("profile") or {}
    if not isinstance(profile, dict):
        profile = {}
    return save_client_business_profile(session_token, profile)
'''

if '"/client/business-profile"' not in main_text:
    insert_before = '\n@app.get("/client/integrations/catalogue")'
    if insert_before in main_text:
        main_text = main_text.replace(insert_before, routes_block + insert_before, 1)
    else:
        main_text += routes_block

MAIN.write_text(main_text, encoding="utf-8")

FRONTEND_API_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_API.write_text(r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://api.trance-formation.com.au";

function backendHeaders() {
  return {
    "Content-Type": "application/json",
    "x-tenant-id": "client_business_profile",
    "x-actor-role": "customer",
    "Origin": "https://ecommerce-ai-agent-platform.vercel.app",
    "Referer": "https://ecommerce-ai-agent-platform.vercel.app/client",
  };
}

export async function GET(request: NextRequest) {
  const sessionToken = request.cookies.get("client_session")?.value || "";

  if (!sessionToken) {
    return NextResponse.json(
      { success: false, error: "client_session_required" },
      { status: 401 }
    );
  }

  const response = await fetch(
    `${BACKEND_URL}/client/business-profile?session_token=${encodeURIComponent(sessionToken)}`,
    {
      method: "GET",
      headers: backendHeaders(),
      cache: "no-store",
    }
  );

  const result = await response.json().catch(() => ({
    success: false,
    error: "business_profile_backend_response_not_json",
  }));

  return NextResponse.json(result, { status: response.ok ? 200 : response.status });
}

export async function POST(request: NextRequest) {
  const sessionToken = request.cookies.get("client_session")?.value || "";

  if (!sessionToken) {
    return NextResponse.json(
      { success: false, error: "client_session_required" },
      { status: 401 }
    );
  }

  const body = await request.json().catch(() => ({}));
  const profile = body?.profile || {};

  const response = await fetch(`${BACKEND_URL}/client/business-profile`, {
    method: "POST",
    headers: backendHeaders(),
    body: JSON.stringify({
      session_token: sessionToken,
      profile,
    }),
    cache: "no-store",
  });

  const result = await response.json().catch(() => ({
    success: false,
    error: "business_profile_backend_response_not_json",
  }));

  return NextResponse.json(result, { status: response.ok ? 200 : response.status });
}
''', encoding="utf-8")

print("CLIENT_BUSINESS_PROFILE_RUNTIME_INSTALLED")
print(f"Created/updated: {RUNTIME}")
print(f"Created/updated: {FRONTEND_API}")