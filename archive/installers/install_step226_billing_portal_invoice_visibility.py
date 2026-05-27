from pathlib import Path
from datetime import datetime, timezone
import py_compile

ROOT = Path.cwd()
CORE = ROOT / "backend" / "app" / "core"
API = ROOT / "backend" / "app" / "api"
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUPS = ROOT / "backups"

CORE.mkdir(parents=True, exist_ok=True)
API.mkdir(parents=True, exist_ok=True)
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_file = CORE / "stripe_customer_billing_portal.py"
routes_file = API / "stripe_customer_billing_routes.py"
test_file = ROOT / "test_step226_customer_billing_portal_invoice_lock.py"
stripe_runner = ROOT / "test_step226_final_stripe_lock_suite.py"

for file in [runtime_file, routes_file, MAIN, test_file, stripe_runner]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step226_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

runtime_file.write_text(r'''
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.app.core.durable_billing_state_store import get_billing_runtime_state
from backend.app.core.stripe_tenant_mapping_store import list_stripe_tenant_mappings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_bool(value: Any) -> bool:
    return bool(value)


def _find_mapping_for_tenant(tenant_id: str) -> Optional[Dict[str, Any]]:
    mappings = list_stripe_tenant_mappings(limit=500).get("mappings", [])
    for item in mappings:
        if item.get("tenant_id") == tenant_id:
            return item
    return None


def customer_billing_visibility(tenant_id: str) -> Dict[str, Any]:
    mapping = _find_mapping_for_tenant(tenant_id)
    runtime_state = get_billing_runtime_state(tenant_id=tenant_id)

    state = runtime_state.get("state") or {}

    subscription_status = (
        state.get("subscription_status")
        or (mapping or {}).get("subscription_status")
        or "unknown"
    )

    client_execution_allowed = state.get("client_execution_allowed")
    credit_state = state.get("credit_state")
    execution_block_reason = state.get("execution_block_reason")
    retry_interval_hours = state.get("retry_interval_hours")

    failed_payment_warning = subscription_status in {"past_due", "unpaid", "payment_failed"} or credit_state == "blocked"

    return {
        "success": True,
        "tenant_id": tenant_id,
        "billing_visibility": {
            "subscription_status": subscription_status,
            "package_name": (mapping or {}).get("package_name"),
            "client_execution_allowed": client_execution_allowed,
            "credit_state": credit_state,
            "execution_block_reason": execution_block_reason,
            "failed_payment_warning": failed_payment_warning,
            "retry_interval_hours": retry_interval_hours,
            "month_to_month": True,
            "lock_in_contract": False,
            "owner_admin_access_unaffected": True,
            "next_billing_date": state.get("current_period_end") or state.get("next_billing_date"),
            "last_webhook_processed_at": state.get("last_webhook_processed_at"),
        },
        "stripe_mapping": {
            "mapping_available": mapping is not None,
            "stripe_customer_id_present": bool((mapping or {}).get("stripe_customer_id")),
            "stripe_subscription_id_present": bool((mapping or {}).get("stripe_subscription_id")),
            "credential_values_exposed": False,
        },
        "invoices": {
            "available": False,
            "reason": "stripe_live_invoice_fetch_requires_configured_stripe_credentials",
            "safe_placeholder": True,
            "credential_values_exposed": False,
        },
        "checked_at": utc_now_iso(),
    }


def billing_portal_readiness(tenant_id: str) -> Dict[str, Any]:
    mapping = _find_mapping_for_tenant(tenant_id)
    stripe_secret_configured = bool(os.getenv("STRIPE_SECRET_KEY"))
    return_url = os.getenv("STRIPE_BILLING_PORTAL_RETURN_URL")

    try:
        import stripe  # type: ignore
        stripe_sdk_available = True
    except Exception:
        stripe_sdk_available = False

    return {
        "success": True,
        "tenant_id": tenant_id,
        "stripe_sdk_available": stripe_sdk_available,
        "stripe_secret_key_configured": stripe_secret_configured,
        "return_url_configured": bool(return_url),
        "stripe_customer_mapping_available": bool(mapping and mapping.get("stripe_customer_id")),
        "ready_for_live_billing_portal": bool(
            stripe_sdk_available
            and stripe_secret_configured
            and return_url
            and mapping
            and mapping.get("stripe_customer_id")
        ),
        "credential_values_exposed": False,
        "checked_at": utc_now_iso(),
    }


def create_customer_billing_portal_session(tenant_id: str) -> Dict[str, Any]:
    mapping = _find_mapping_for_tenant(tenant_id)
    readiness = billing_portal_readiness(tenant_id)

    if not mapping or not mapping.get("stripe_customer_id"):
        return {
            "success": False,
            "status": "billing_portal_not_created",
            "reason": "stripe_customer_mapping_missing",
            "tenant_id": tenant_id,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    if not readiness.get("stripe_secret_key_configured"):
        return {
            "success": False,
            "status": "billing_portal_not_created",
            "reason": "stripe_secret_key_not_configured",
            "tenant_id": tenant_id,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    if not readiness.get("stripe_sdk_available"):
        return {
            "success": False,
            "status": "billing_portal_not_created",
            "reason": "stripe_sdk_not_installed",
            "tenant_id": tenant_id,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    return_url = os.getenv("STRIPE_BILLING_PORTAL_RETURN_URL")
    if not return_url:
        return {
            "success": False,
            "status": "billing_portal_not_created",
            "reason": "stripe_billing_portal_return_url_missing",
            "tenant_id": tenant_id,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    try:
        import stripe  # type: ignore

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        session = stripe.billing_portal.Session.create(
            customer=mapping["stripe_customer_id"],
            return_url=return_url,
        )

        return {
            "success": True,
            "status": "billing_portal_session_created",
            "tenant_id": tenant_id,
            "portal_url": getattr(session, "url", None),
            "stripe_customer_id_present": True,
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": "billing_portal_creation_failed",
            "reason": type(exc).__name__,
            "safe_message": str(exc),
            "tenant_id": tenant_id,
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }
'''.lstrip(), encoding="utf-8")

routes_file.write_text(r'''
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header

from backend.app.core.stripe_customer_billing_portal import (
    billing_portal_readiness,
    create_customer_billing_portal_session,
    customer_billing_visibility,
)

router = APIRouter()


def _is_owner_admin(role: Optional[str]) -> bool:
    return role in {"owner", "admin", "system"}


@router.get("/customer/billing/visibility")
async def customer_billing_visibility_route(
    tenant_id: str,
    x_tenant_id: Optional[str] = Header(default=None),
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _is_owner_admin(x_actor_role) and x_tenant_id != tenant_id:
        return {
            "success": False,
            "error": "tenant_access_denied",
        }

    return customer_billing_visibility(tenant_id)


@router.get("/admin/billing/customer-portal-readiness")
async def admin_billing_portal_readiness(
    tenant_id: str,
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _is_owner_admin(x_actor_role):
        return {
            "success": False,
            "error": "owner_admin_required",
        }

    return billing_portal_readiness(tenant_id)


@router.post("/admin/billing/create-customer-portal-session")
async def admin_create_customer_billing_portal_session(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _is_owner_admin(x_actor_role):
        return {
            "success": False,
            "error": "owner_admin_required",
        }

    tenant_id = str(payload.get("tenant_id") or "").strip()
    if not tenant_id:
        return {
            "success": False,
            "error": "tenant_id_required",
        }

    return create_customer_billing_portal_session(tenant_id)
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")
include_block = '''
# Step 226 Stripe customer billing visibility routes
try:
    from backend.app.api.stripe_customer_billing_routes import router as stripe_customer_billing_router
    app.include_router(stripe_customer_billing_router)
except Exception as exc:
    print(f"STEP_226_STRIPE_CUSTOMER_BILLING_ROUTES_NOT_LOADED: {exc}")
'''
if "stripe_customer_billing_router" not in main_text:
    main_text = main_text.rstrip() + "\n\n" + include_block.lstrip() + "\n"
MAIN.write_text(main_text, encoding="utf-8")

test_file.write_text(r'''
import json
import urllib.request

BASE = "http://127.0.0.1:8000"
TENANT_ID = "client_step223_001"


def request_json(path, method="GET", payload=None, tenant_header="owner", role="owner"):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-tenant-id": tenant_header,
            "x-actor-role": role,
        },
        method=method,
    )

    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


visibility = request_json(f"/customer/billing/visibility?tenant_id={TENANT_ID}")
readiness = request_json(f"/admin/billing/customer-portal-readiness?tenant_id={TENANT_ID}")
portal_attempt = request_json(
    "/admin/billing/create-customer-portal-session",
    method="POST",
    payload={"tenant_id": TENANT_ID},
)

combined_text = json.dumps({
    "visibility": visibility,
    "readiness": readiness,
    "portal_attempt": portal_attempt,
}).lower()

checks = {
    "visibility_success": visibility.get("success") is True,
    "billing_visibility_present": isinstance(visibility.get("billing_visibility"), dict),
    "month_to_month_visible": visibility.get("billing_visibility", {}).get("month_to_month") is True,
    "no_lock_in_visible": visibility.get("billing_visibility", {}).get("lock_in_contract") is False,
    "mapping_available": visibility.get("stripe_mapping", {}).get("mapping_available") is True,
    "customer_id_presence_only": visibility.get("stripe_mapping", {}).get("stripe_customer_id_present") is True,
    "subscription_id_presence_only": visibility.get("stripe_mapping", {}).get("stripe_subscription_id_present") is True,
    "invoice_visibility_safe_placeholder": visibility.get("invoices", {}).get("safe_placeholder") is True,
    "portal_readiness_success": readiness.get("success") is True,
    "portal_attempt_controlled": portal_attempt.get("status") in {
        "billing_portal_not_created",
        "billing_portal_session_created",
        "billing_portal_creation_failed",
    },
    "no_secret_values_exposed": all(secret not in combined_text for secret in [
        "sk_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_226_CUSTOMER_BILLING_PORTAL_INVOICE_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "visibility": visibility,
        "readiness": readiness,
        "portal_attempt": portal_attempt,
    }, indent=2))
    raise SystemExit(1)

print("STEP_226_CUSTOMER_BILLING_PORTAL_INVOICE_LOCK_OK")
'''.lstrip(), encoding="utf-8")

stripe_runner.write_text(r'''
import subprocess
import sys

tests = [
    "test_step222_stripe_checkout_endpoint_lock.py",
    "test_step223_checkout_completed_mapping_lock.py",
    "test_step224_stripe_webhook_signature_lock.py",
    "test_step225_cancel_reactivate_durable_sync_lock.py",
    "test_step226_customer_billing_portal_invoice_lock.py",
    "test_step217_stripe_webhook_lifecycle_lock.py",
]

print("STEP_226_FINAL_STRIPE_LOCK_SUITE")
failed = []

for test in tests:
    print(f"\nRUNNING {test}")
    result = subprocess.run([sys.executable, test], text=True)
    print(f"RESULT {test}: exit_code={result.returncode}")

    if result.returncode != 0:
        failed.append(test)

if failed:
    print("\nSTEP_226_FINAL_STRIPE_LOCK_FAILED")
    print("FAILED_TESTS", failed)
    raise SystemExit(1)

print("\nSTEP_226_FINAL_STRIPE_LOCK_SUITE_OK")
'''.lstrip(), encoding="utf-8")

for file in [runtime_file, routes_file, MAIN, test_file, stripe_runner]:
    py_compile.compile(str(file), doraise=True)

print("STEP_226_BILLING_PORTAL_INVOICE_VISIBILITY_INSTALLED")
print(f"Created/updated: {runtime_file}")
print(f"Created/updated: {routes_file}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {test_file}")
print(f"Created/updated: {stripe_runner}")
print("STEP_226_OK")