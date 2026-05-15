import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

import psycopg


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

    with get_connection() as conn:
        with conn.cursor() as cur:
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


initialise_tables()
