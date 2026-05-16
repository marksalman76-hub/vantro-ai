import json
import os
from datetime import datetime, timezone

import psycopg


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL_missing")
    return psycopg.connect(DATABASE_URL)


def initialise_billing_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS client_subscriptions (
                tenant_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                company_name TEXT,
                package_name TEXT NOT NULL,
                billing_cycle TEXT NOT NULL,
                billing_status TEXT NOT NULL,
                monthly_credits INTEGER NOT NULL DEFAULT 0,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                stripe_price_id TEXT,
                current_period_start TIMESTAMPTZ,
                current_period_end TIMESTAMPTZ,
                next_billing_date TIMESTAMPTZ,
                cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS client_billing_events (
                id SERIAL PRIMARY KEY,
                tenant_id TEXT,
                email TEXT,
                event_type TEXT NOT NULL,
                provider TEXT NOT NULL,
                provider_event_id TEXT,
                payload TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL
            )
            """)

        conn.commit()


BILLING_STARTUP_STATUS = {
    "available": False,
    "initialised": False,
    "error": None,
}


def safe_initialise_billing_tables():
    try:
        initialise_billing_tables()
        BILLING_STARTUP_STATUS["available"] = True
        BILLING_STARTUP_STATUS["initialised"] = True
        BILLING_STARTUP_STATUS["error"] = None
    except Exception as exc:
        BILLING_STARTUP_STATUS["available"] = False
        BILLING_STARTUP_STATUS["initialised"] = False
        BILLING_STARTUP_STATUS["error"] = str(exc)


def billing_readiness():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()

        return {
            "success": True,
            "billing_database_available": True,
            "startup_status": BILLING_STARTUP_STATUS,
            "test_result": row[0] if row else None,
            "billing_model": {
                "card_storage": "stripe_tokenised_storage_only",
                "local_card_storage": False,
                "monthly_subscription_rebilling": True,
                "invoice_email_provider": "stripe",
                "credit_reset_on_successful_invoice": True,
                "client_suspension_on_credit_exhaustion": True,
            },
        }
    except Exception as exc:
        return {
            "success": False,
            "billing_database_available": False,
            "startup_status": BILLING_STARTUP_STATUS,
            "error": str(exc),
        }


def upsert_subscription(payload: dict):
    now = datetime.now(timezone.utc)

    tenant_id = str(payload.get("tenant_id") or "").strip()
    email = str(payload.get("email") or "").strip().lower()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    if not email:
        return {"success": False, "error": "email_required"}

    package_name = str(payload.get("package") or payload.get("package_name") or "trial")
    billing_cycle = str(payload.get("billing_cycle") or "monthly")
    billing_status = str(payload.get("billing_status") or "active")
    monthly_credits = int(payload.get("monthly_credits") or 0)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client_subscriptions (
                tenant_id,
                email,
                company_name,
                package_name,
                billing_cycle,
                billing_status,
                monthly_credits,
                stripe_customer_id,
                stripe_subscription_id,
                stripe_price_id,
                current_period_start,
                current_period_end,
                next_billing_date,
                cancel_at_period_end,
                created_at,
                updated_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (tenant_id)
            DO UPDATE SET
                email = EXCLUDED.email,
                company_name = EXCLUDED.company_name,
                package_name = EXCLUDED.package_name,
                billing_cycle = EXCLUDED.billing_cycle,
                billing_status = EXCLUDED.billing_status,
                monthly_credits = EXCLUDED.monthly_credits,
                stripe_customer_id = EXCLUDED.stripe_customer_id,
                stripe_subscription_id = EXCLUDED.stripe_subscription_id,
                stripe_price_id = EXCLUDED.stripe_price_id,
                current_period_start = EXCLUDED.current_period_start,
                current_period_end = EXCLUDED.current_period_end,
                next_billing_date = EXCLUDED.next_billing_date,
                cancel_at_period_end = EXCLUDED.cancel_at_period_end,
                updated_at = EXCLUDED.updated_at
            RETURNING tenant_id, email, company_name, package_name, billing_cycle, billing_status, monthly_credits, next_billing_date, cancel_at_period_end
            """, (
                tenant_id,
                email,
                payload.get("company_name"),
                package_name,
                billing_cycle,
                billing_status,
                monthly_credits,
                payload.get("stripe_customer_id"),
                payload.get("stripe_subscription_id"),
                payload.get("stripe_price_id"),
                payload.get("current_period_start"),
                payload.get("current_period_end"),
                payload.get("next_billing_date"),
                bool(payload.get("cancel_at_period_end", False)),
                now,
                now,
            ))

            row = cur.fetchone()

        conn.commit()

    return {
        "success": True,
        "subscription": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "billing_cycle": row[4],
            "billing_status": row[5],
            "monthly_credits": row[6],
            "next_billing_date": row[7].isoformat() if row[7] else None,
            "cancel_at_period_end": row[8],
        },
        "card_storage": "stripe_tokenised_storage_only",
        "local_card_storage": False,
    }


def record_billing_event(payload: dict):
    now = datetime.now(timezone.utc)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client_billing_events (
                tenant_id,
                email,
                event_type,
                provider,
                provider_event_id,
                payload,
                created_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
            """, (
                payload.get("tenant_id"),
                payload.get("email"),
                str(payload.get("event_type") or "billing_event"),
                str(payload.get("provider") or "stripe"),
                payload.get("provider_event_id"),
                json.dumps(payload),
                now,
            ))

            row = cur.fetchone()

        conn.commit()

    return {
        "success": True,
        "billing_event_id": row[0],
        "stored": True,
    }


def get_subscription(identifier: str):
    identifier = str(identifier or "").strip().lower()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT tenant_id, email, company_name, package_name, billing_cycle, billing_status, monthly_credits, next_billing_date, cancel_at_period_end
            FROM client_subscriptions
            WHERE lower(tenant_id) = %s OR lower(email) = %s
            """, (identifier, identifier))

            row = cur.fetchone()

    if not row:
        return {"success": False, "error": "subscription_not_found"}

    return {
        "success": True,
        "subscription": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "billing_cycle": row[4],
            "billing_status": row[5],
            "monthly_credits": row[6],
            "next_billing_date": row[7].isoformat() if row[7] else None,
            "cancel_at_period_end": row[8],
        },
    }


safe_initialise_billing_tables()


def handle_invoice_payment_succeeded(payload: dict):
    tenant_id = str(payload.get("tenant_id") or "").strip()
    provider_event_id = payload.get("provider_event_id")

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    subscription = get_subscription(tenant_id)

    if not subscription.get("success"):
        return {"success": False, "error": "subscription_not_found"}

    monthly_credits = int(subscription["subscription"].get("monthly_credits") or 0)

    from backend.app.core.postgres_account_runtime import assign_client_credits

    credit_result = assign_client_credits({
        "tenant_id": tenant_id,
        "monthly_credits": monthly_credits,
        "top_up_credits": 0,
    })

    event_result = record_billing_event({
        "tenant_id": tenant_id,
        "email": subscription["subscription"].get("email"),
        "event_type": "invoice.payment_succeeded",
        "provider": "stripe",
        "provider_event_id": provider_event_id,
        "credit_reset": credit_result,
        "invoice_email_provider": "stripe",
        "local_card_storage": False,
    })

    return {
        "success": True,
        "billing_event": "invoice.payment_succeeded",
        "tenant_id": tenant_id,
        "monthly_credits_reset_to": monthly_credits,
        "credit_reset": credit_result,
        "event_record": event_result,
        "invoice_email_provider": "stripe",
        "local_card_storage": False,
    }


def handle_invoice_payment_failed(payload: dict):
    tenant_id = str(payload.get("tenant_id") or "").strip()
    provider_event_id = payload.get("provider_event_id")

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    subscription = get_subscription(tenant_id)

    if not subscription.get("success"):
        return {"success": False, "error": "subscription_not_found"}

    now = datetime.now(timezone.utc)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE client_subscriptions
            SET billing_status = %s,
                updated_at = %s
            WHERE tenant_id = %s
            RETURNING tenant_id, email, company_name, package_name, billing_cycle, billing_status, monthly_credits, next_billing_date, cancel_at_period_end
            """, (
                "past_due",
                now,
                tenant_id,
            ))

            row = cur.fetchone()

        conn.commit()

    event_result = record_billing_event({
        "tenant_id": tenant_id,
        "email": subscription["subscription"].get("email"),
        "event_type": "invoice.payment_failed",
        "provider": "stripe",
        "provider_event_id": provider_event_id,
        "billing_status": "past_due",
        "invoice_email_provider": "stripe",
        "local_card_storage": False,
        "client_visible_status": "payment_attention_required",
    })

    return {
        "success": True,
        "billing_event": "invoice.payment_failed",
        "tenant_id": tenant_id,
        "subscription": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "billing_cycle": row[4],
            "billing_status": row[5],
            "monthly_credits": row[6],
            "next_billing_date": row[7].isoformat() if row[7] else None,
            "cancel_at_period_end": row[8],
        },
        "event_record": event_result,
        "invoice_email_provider": "stripe",
        "local_card_storage": False,
        "client_visible_status": "payment_attention_required",
        "execution_policy": "credit_consuming_actions_may_be_blocked_if_payment_remains_unresolved",
    }

