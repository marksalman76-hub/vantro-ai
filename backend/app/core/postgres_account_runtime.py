import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

import psycopg

from backend.app.core.canonical_billing_state_runtime import owner_admin_bypasses_client_billing


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL_missing")

    return psycopg.connect(DATABASE_URL)


def initialise_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS client_activation_invites (
                token TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                email TEXT NOT NULL,
                company_name TEXT,
                package_name TEXT,
                active_agents TEXT,
                created_at TIMESTAMPTZ NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL,
                used BOOLEAN NOT NULL DEFAULT FALSE
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS client_accounts (
                tenant_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                company_name TEXT,
                package_name TEXT,
                active_agents TEXT,
                password_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL,
                activated_at TIMESTAMPTZ NOT NULL,
                monthly_credits INTEGER NOT NULL DEFAULT 0,
                credits_used INTEGER NOT NULL DEFAULT 0
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS client_sessions (
                session_token TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS client_security_events (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMPTZ NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT NOT NULL
            )
            """)

        conn.commit()


def hash_password(password: str):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        b"ecommerce_ai_platform",
        100000
    ).hex()


def verify_password(password: str, stored_hash: str):
    return hash_password(password) == stored_hash


def log_security_event(event_type: str, details: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client_security_events (
                created_at,
                event_type,
                details
            )
            VALUES (%s, %s, %s)
            """, (
                datetime.now(timezone.utc),
                event_type,
                json.dumps(details)
            ))

        conn.commit()


def create_activation_invite(payload: dict):
    token = secrets.token_urlsafe(48)

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=3)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client_activation_invites (
                token,
                tenant_id,
                email,
                company_name,
                package_name,
                active_agents,
                created_at,
                expires_at,
                used
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                token,
                payload["tenant_id"],
                payload["email"],
                payload.get("company_name"),
                payload.get("package"),
                json.dumps(payload.get("active_agents", [])),
                now,
                expires_at,
                False
            ))

        conn.commit()

    return {
        "success": True,
        "tenant_id": payload["tenant_id"],
        "email": payload["email"],
        "activation_token": token,
        "activation_path": f"/activate?token={token}",
        "expires_at": expires_at.isoformat(),
    }


def get_activation_invite(token: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT
                tenant_id,
                email,
                company_name,
                package_name,
                active_agents,
                created_at,
                expires_at,
                used
            FROM client_activation_invites
            WHERE token = %s
            """, (token,))

            row = cur.fetchone()

    if not row:
        return None

    return {
        "tenant_id": row[0],
        "email": row[1],
        "company_name": row[2],
        "package": row[3],
        "active_agents": json.loads(row[4] or "[]"),
        "created_at": row[5],
        "expires_at": row[6],
        "used": row[7],
    }


def activate_account(token: str, password: str):
    invite = get_activation_invite(token)

    if not invite:
        return {"success": False, "error": "invalid_activation_token"}

    if invite["used"]:
        return {"success": False, "error": "activation_link_already_used"}

    now = datetime.now(timezone.utc)

    if invite["expires_at"] < now:
        return {"success": False, "error": "activation_link_expired"}

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Re-issued activation links for the same client/email must not crash
                # on tenant_id/email uniqueness. Replace the previous pending/active
                # account record for this same client identity, then activate fresh.
                cur.execute("""
                DELETE FROM client_accounts
                WHERE tenant_id = %s OR lower(email) = lower(%s)
                """, (
                    invite["tenant_id"],
                    invite["email"],
                ))

                cur.execute("""
                INSERT INTO client_accounts (
                    tenant_id,
                    email,
                    company_name,
                    package_name,
                    active_agents,
                    password_hash,
                    status,
                    created_at,
                    activated_at,
                    monthly_credits,
                    credits_used
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    invite["tenant_id"],
                    invite["email"],
                    invite["company_name"],
                    invite["package"],
                    json.dumps(invite["active_agents"]),
                    hash_password(password),
                    "active",
                    now,
                    now,
                    0,
                    0
                ))

                cur.execute("""
                UPDATE client_activation_invites
                SET used = TRUE
                WHERE token = %s
                """, (token,))

            conn.commit()
    except Exception as exc:
        return {
            "success": False,
            "error": "account_activation_database_error",
            "details": str(exc),
        }

    return {
        "success": True,
        "account": {
            "tenant_id": invite["tenant_id"],
            "email": invite["email"],
            "company_name": invite["company_name"],
            "package": invite["package"],
            "active_agents": invite["active_agents"],
            "status": "active",
        }
    }


def login(email: str, password: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT
                tenant_id,
                email,
                company_name,
                package_name,
                active_agents,
                password_hash,
                status,
                monthly_credits,
                credits_used
            FROM client_accounts
            WHERE email = %s
            """, (email,))

            row = cur.fetchone()

    if not row:
        log_security_event(
            "failed_login_unknown_or_inactive_account",
            {"email": email}
        )

        return {"success": False, "error": "invalid_login"}

    stored_hash = row[5]

    if not verify_password(password, stored_hash):
        log_security_event(
            "failed_login_invalid_password",
            {"email": email}
        )

        return {"success": False, "error": "invalid_login"}

    session_token = secrets.token_urlsafe(48)

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=8)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client_sessions (
                session_token,
                tenant_id,
                email,
                created_at,
                expires_at
            )
            VALUES (%s,%s,%s,%s,%s)
            """, (
                session_token,
                row[0],
                row[1],
                now,
                expires_at
            ))

        conn.commit()

    return {
        "success": True,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "account": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "active_agents": json.loads(row[4] or "[]"),
            "status": row[6],
            "monthly_credits": row[7],
            "credits_used": row[8],
        }
    }


def get_session_account(session_token: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT
                s.tenant_id,
                a.email,
                a.company_name,
                a.package_name,
                a.active_agents,
                a.status,
                a.monthly_credits,
                a.credits_used,
                s.expires_at
            FROM client_sessions s
            JOIN client_accounts a
                ON a.tenant_id = s.tenant_id
            WHERE s.session_token = %s
            """, (session_token,))

            row = cur.fetchone()

    if not row:
        return {"success": False, "error": "invalid_session"}

    now = datetime.now(timezone.utc)

    if row[8] < now:
        return {"success": False, "error": "session_expired"}

    return {
        "success": True,
        "account": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "active_agents": json.loads(row[4] or "[]"),
            "status": row[5],
            "monthly_credits": row[6],
            "credits_used": row[7],
        }
    }


def recent_security_events(limit: int = 10):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT
                created_at,
                event_type,
                details
            FROM client_security_events
            ORDER BY created_at DESC
            LIMIT %s
            """, (limit,))

            rows = cur.fetchall()

    return {
        "success": True,
        "events": [
            {
                "created_at": row[0].isoformat(),
                "event_type": row[1],
                "details": json.loads(row[2]),
            }
            for row in rows
        ]
    }



POSTGRES_STARTUP_STATUS = {
    "available": False,
    "initialised": False,
    "error": None,
}


def safe_initialise_tables():
    try:
        initialise_tables()
        POSTGRES_STARTUP_STATUS["available"] = True
        POSTGRES_STARTUP_STATUS["initialised"] = True
        POSTGRES_STARTUP_STATUS["error"] = None
    except Exception as exc:
        POSTGRES_STARTUP_STATUS["available"] = False
        POSTGRES_STARTUP_STATUS["initialised"] = False
        POSTGRES_STARTUP_STATUS["error"] = str(exc)


def database_readiness():
    raw = DATABASE_URL or ""

    safe_url_details = {
        "database_url_present": bool(raw),
        "length": len(raw),
        "starts_with_postgresql": raw.startswith("postgresql://"),
        "contains_placeholder": "[YOUR-PASSWORD]" in raw,
        "contains_spaces": " " in raw,
        "contains_pooler_host": "pooler.supabase.com" in raw,
        "contains_project_ref_username": "postgres.udcvkzgxojklwwdocokv" in raw,
        "contains_direct_host": "db.udcvkzgxojklwwdocokv.supabase.co" in raw,
        "contains_at_symbol": "@" in raw,
        "contains_database_suffix": raw.endswith("/postgres"),
    }

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()

        return {
            "success": True,
            "database_available": True,
            "startup_status": POSTGRES_STARTUP_STATUS,
            "database_url_details": safe_url_details,
            "test_result": row[0] if row else None,
        }
    except Exception as exc:
        return {
            "success": False,
            "database_available": False,
            "startup_status": POSTGRES_STARTUP_STATUS,
            "database_url_details": safe_url_details,
            "error": str(exc),
        }


safe_initialise_tables()


def assign_client_credits(payload: dict):
    tenant_id = str(payload.get("tenant_id") or "").strip()
    monthly_credits = int(payload.get("monthly_credits") or 0)
    top_up_credits = int(payload.get("top_up_credits") or 0)

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE client_accounts
            SET monthly_credits = %s,
                credits_used = GREATEST(credits_used - %s, 0)
            WHERE tenant_id = %s
            RETURNING tenant_id, email, company_name, package_name, active_agents, status, monthly_credits, credits_used
            """, (
                monthly_credits,
                top_up_credits,
                tenant_id,
            ))

            row = cur.fetchone()

        conn.commit()

    if not row:
        return {"success": False, "error": "client_account_not_found"}

    return {
        "success": True,
        "account": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "active_agents": json.loads(row[4] or "[]"),
            "status": row[5],
            "monthly_credits": row[6],
            "credits_used": row[7],
            "credits_remaining": max(int(row[6]) - int(row[7]), 0),
        },
    }


def lookup_client_account(identifier: str):
    identifier = str(identifier or "").strip().lower()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT
                tenant_id,
                email,
                company_name,
                package_name,
                active_agents,
                status,
                monthly_credits,
                credits_used
            FROM client_accounts
            WHERE lower(tenant_id) = %s OR lower(email) = %s
            """, (identifier, identifier))

            row = cur.fetchone()

    if not row:
        return {"success": False, "error": "client_account_not_found", "identifier": identifier}

    return {
        "success": True,
        "account": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "active_agents": json.loads(row[4] or "[]"),
            "status": row[5],
            "monthly_credits": row[6],
            "credits_used": row[7],
            "credits_remaining": max(int(row[6]) - int(row[7]), 0),
        },
    }


def client_credit_gate(payload: dict):
    actor_role = str(payload.get("actor_role") or "client").strip().lower()

    if owner_admin_bypasses_client_billing(actor_role):
        return {
            "success": True,
            "credit_gate_passed": True,
            "bypass_reason": "owner_admin_system_execution_unrestricted_by_client_credits",
            "credits_required": False,
        }

    tenant_id = str(payload.get("tenant_id") or "").strip()
    requested_credits = int(payload.get("requested_credits") or 1)

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT monthly_credits, credits_used
            FROM client_accounts
            WHERE tenant_id = %s AND status = 'active'
            """, (tenant_id,))

            row = cur.fetchone()

    if not row:
        return {
            "success": False,
            "credit_gate_passed": False,
            "error": "active_client_account_not_found",
        }

    monthly_credits = int(row[0] or 0)
    credits_used = int(row[1] or 0)
    credits_remaining = max(monthly_credits - credits_used, 0)

    if credits_remaining <= 0:
        return {
            "success": False,
            "credit_gate_passed": False,
            "error": "client_monthly_credits_exhausted",
            "execution_status": "blocked_until_top_up_or_next_billing_cycle",
            "monthly_credits": monthly_credits,
            "credits_used": credits_used,
            "credits_remaining": credits_remaining,
            "top_up_required": True,
        }

    if requested_credits > credits_remaining:
        return {
            "success": False,
            "credit_gate_passed": False,
            "error": "insufficient_client_credits",
            "execution_status": "blocked_until_top_up_or_next_billing_cycle",
            "monthly_credits": monthly_credits,
            "credits_used": credits_used,
            "credits_remaining": credits_remaining,
            "requested_credits": requested_credits,
            "top_up_required": True,
        }

    return {
        "success": True,
        "credit_gate_passed": True,
        "credits_required": True,
        "monthly_credits": monthly_credits,
        "credits_used": credits_used,
        "credits_remaining": credits_remaining,
        "requested_credits": requested_credits,
    }

