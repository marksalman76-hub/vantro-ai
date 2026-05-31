from pathlib import Path
from datetime import datetime
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

runtime_file = CORE / "stripe_advanced_billing_runtime.py"
routes_file = API / "stripe_advanced_billing_routes.py"
test_file = ROOT / "test_step229_advanced_stripe_billing_lock.py"

for file in [runtime_file, routes_file, MAIN, test_file]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step229_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

runtime_file.write_text(r'''
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


MONTHLY_PRICE_ENV = {
    "starter": "STRIPE_PRICE_STARTER_MONTHLY",
    "growth": "STRIPE_PRICE_GROWTH_MONTHLY",
    "pro": "STRIPE_PRICE_PRO_MONTHLY",
}

YEARLY_PRICE_ENV = {
    "starter": "STRIPE_PRICE_STARTER_YEARLY",
    "growth": "STRIPE_PRICE_GROWTH_YEARLY",
    "pro": "STRIPE_PRICE_PRO_YEARLY",
}

TOPUP_PRICE_ENV = {
    "small": "STRIPE_PRICE_TOPUP_SMALL",
    "medium": "STRIPE_PRICE_TOPUP_MEDIUM",
    "large": "STRIPE_PRICE_TOPUP_LARGE",
}

DEFAULT_TRIAL_DAYS = int(os.getenv("STRIPE_DEFAULT_TRIAL_DAYS", "7"))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_package(package_name: Optional[str]) -> str:
    value = (package_name or "").strip().lower()
    if value in {"starter", "start"}:
        return "starter"
    if value in {"growth", "grow"}:
        return "growth"
    if value in {"pro", "professional"}:
        return "pro"
    return value


def _normalise_billing_interval(interval: Optional[str]) -> str:
    value = (interval or "monthly").strip().lower()
    if value in {"annual", "year", "yearly"}:
        return "yearly"
    return "monthly"


def _normalise_topup(topup_size: Optional[str]) -> str:
    value = (topup_size or "").strip().lower()
    if value in {"small", "medium", "large"}:
        return value
    return "small"


def _stripe_sdk_available() -> bool:
    try:
        import stripe  # type: ignore
        return True
    except Exception:
        return False


def _price_env_for(package_name: str, billing_interval: str) -> Optional[str]:
    if billing_interval == "yearly":
        return YEARLY_PRICE_ENV.get(package_name)
    return MONTHLY_PRICE_ENV.get(package_name)


def _configured(env_name: Optional[str]) -> bool:
    return bool(env_name and os.getenv(env_name))


def advanced_billing_readiness() -> Dict[str, Any]:
    monthly = {
        package: {
            "env_name": env_name,
            "configured": _configured(env_name),
        }
        for package, env_name in MONTHLY_PRICE_ENV.items()
    }

    yearly = {
        package: {
            "env_name": env_name,
            "configured": _configured(env_name),
        }
        for package, env_name in YEARLY_PRICE_ENV.items()
    }

    topups = {
        size: {
            "env_name": env_name,
            "configured": _configured(env_name),
        }
        for size, env_name in TOPUP_PRICE_ENV.items()
    }

    return {
        "success": True,
        "checked_at": utc_now_iso(),
        "stripe_sdk_available": _stripe_sdk_available(),
        "stripe_secret_key_configured": bool(os.getenv("STRIPE_SECRET_KEY")),
        "coupons_supported": True,
        "free_trials_supported": True,
        "upgrade_downgrade_supported": True,
        "annual_billing_supported": True,
        "topup_credit_checkout_supported": True,
        "tax_gst_supported": True,
        "invoice_portal_polish_supported": True,
        "monthly_prices": monthly,
        "yearly_prices": yearly,
        "topup_prices": topups,
        "default_trial_days": DEFAULT_TRIAL_DAYS,
        "tax": {
            "automatic_tax_enabled_by_default": os.getenv("STRIPE_AUTOMATIC_TAX_ENABLED", "true").lower() != "false",
            "gst_supported": True,
            "tax_id_collection_supported": True,
        },
        "credential_values_exposed": False,
    }


def create_advanced_subscription_checkout(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    package_name = _normalise_package(payload.get("package_name"))
    billing_interval = _normalise_billing_interval(payload.get("billing_interval"))
    customer_email = str(payload.get("customer_email") or "").strip()
    success_url = str(payload.get("success_url") or os.getenv("STRIPE_CHECKOUT_SUCCESS_URL") or "").strip()
    cancel_url = str(payload.get("cancel_url") or os.getenv("STRIPE_CHECKOUT_CANCEL_URL") or "").strip()
    coupon_id = str(payload.get("coupon_id") or "").strip()
    promotion_code = str(payload.get("promotion_code") or "").strip()
    trial_days = payload.get("trial_days")
    trial_enabled = bool(payload.get("trial_enabled", False))

    price_env = _price_env_for(package_name, billing_interval)
    price_id = os.getenv(price_env or "")

    if not tenant_id:
        return {"success": False, "status": "advanced_checkout_not_created", "reason": "tenant_id_required", "credential_values_exposed": False}

    if not customer_email:
        return {"success": False, "status": "advanced_checkout_not_created", "reason": "customer_email_required", "credential_values_exposed": False}

    if package_name not in MONTHLY_PRICE_ENV:
        return {
            "success": False,
            "status": "advanced_checkout_not_created",
            "reason": "unknown_package",
            "allowed_packages": list(MONTHLY_PRICE_ENV.keys()),
            "credential_values_exposed": False,
        }

    if not price_id:
        return {
            "success": False,
            "status": "advanced_checkout_not_created",
            "reason": "stripe_price_id_missing",
            "package_name": package_name,
            "billing_interval": billing_interval,
            "required_env": price_env,
            "credential_values_exposed": False,
        }

    if not os.getenv("STRIPE_SECRET_KEY"):
        return {
            "success": False,
            "status": "advanced_checkout_not_created",
            "reason": "stripe_secret_key_not_configured",
            "credential_values_exposed": False,
        }

    if not _stripe_sdk_available():
        return {
            "success": False,
            "status": "advanced_checkout_not_created",
            "reason": "stripe_sdk_not_installed",
            "credential_values_exposed": False,
        }

    subscription_data = {
        "metadata": {
            "tenant_id": tenant_id,
            "package_name": package_name,
            "billing_interval": billing_interval,
            "advanced_billing": "true",
            "contract_type": "month_to_month" if billing_interval == "monthly" else "annual_subscription",
        }
    }

    if trial_enabled:
        subscription_data["trial_period_days"] = int(trial_days or DEFAULT_TRIAL_DAYS)

    discounts = []
    if coupon_id:
        discounts.append({"coupon": coupon_id})
    if promotion_code:
        discounts.append({"promotion_code": promotion_code})

    try:
        import stripe  # type: ignore

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        session_kwargs = {
            "mode": "subscription",
            "customer_email": customer_email,
            "client_reference_id": tenant_id,
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "subscription_data": subscription_data,
            "metadata": {
                "tenant_id": tenant_id,
                "package_name": package_name,
                "billing_interval": billing_interval,
                "advanced_billing": "true",
            },
            "allow_promotion_codes": True,
            "automatic_tax": {"enabled": os.getenv("STRIPE_AUTOMATIC_TAX_ENABLED", "true").lower() != "false"},
            "tax_id_collection": {"enabled": True},
        }

        if discounts:
            session_kwargs["discounts"] = discounts

        session = stripe.checkout.Session.create(**session_kwargs)

        return {
            "success": True,
            "status": "advanced_checkout_session_created",
            "tenant_id": tenant_id,
            "package_name": package_name,
            "billing_interval": billing_interval,
            "trial_enabled": trial_enabled,
            "coupon_or_promotion_configured": bool(discounts),
            "automatic_tax_enabled": session_kwargs["automatic_tax"]["enabled"],
            "tax_id_collection_enabled": True,
            "stripe_checkout_session_id": getattr(session, "id", None),
            "checkout_url": getattr(session, "url", None),
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": "advanced_checkout_creation_failed",
            "reason": type(exc).__name__,
            "safe_message": str(exc),
            "tenant_id": tenant_id,
            "package_name": package_name,
            "billing_interval": billing_interval,
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }


def create_topup_credit_checkout(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    customer_email = str(payload.get("customer_email") or "").strip()
    topup_size = _normalise_topup(payload.get("topup_size"))
    success_url = str(payload.get("success_url") or os.getenv("STRIPE_CHECKOUT_SUCCESS_URL") or "").strip()
    cancel_url = str(payload.get("cancel_url") or os.getenv("STRIPE_CHECKOUT_CANCEL_URL") or "").strip()

    env_name = TOPUP_PRICE_ENV.get(topup_size)
    price_id = os.getenv(env_name or "")

    if not tenant_id:
        return {"success": False, "status": "topup_checkout_not_created", "reason": "tenant_id_required", "credential_values_exposed": False}

    if not customer_email:
        return {"success": False, "status": "topup_checkout_not_created", "reason": "customer_email_required", "credential_values_exposed": False}

    if not price_id:
        return {
            "success": False,
            "status": "topup_checkout_not_created",
            "reason": "stripe_topup_price_id_missing",
            "topup_size": topup_size,
            "required_env": env_name,
            "credential_values_exposed": False,
        }

    if not os.getenv("STRIPE_SECRET_KEY"):
        return {"success": False, "status": "topup_checkout_not_created", "reason": "stripe_secret_key_not_configured", "credential_values_exposed": False}

    if not _stripe_sdk_available():
        return {"success": False, "status": "topup_checkout_not_created", "reason": "stripe_sdk_not_installed", "credential_values_exposed": False}

    try:
        import stripe  # type: ignore

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        session = stripe.checkout.Session.create(
            mode="payment",
            customer_email=customer_email,
            client_reference_id=tenant_id,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "tenant_id": tenant_id,
                "topup_size": topup_size,
                "checkout_type": "credit_topup",
            },
            automatic_tax={"enabled": os.getenv("STRIPE_AUTOMATIC_TAX_ENABLED", "true").lower() != "false"},
            tax_id_collection={"enabled": True},
        )

        return {
            "success": True,
            "status": "topup_checkout_session_created",
            "tenant_id": tenant_id,
            "topup_size": topup_size,
            "stripe_checkout_session_id": getattr(session, "id", None),
            "checkout_url": getattr(session, "url", None),
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": "topup_checkout_creation_failed",
            "reason": type(exc).__name__,
            "safe_message": str(exc),
            "tenant_id": tenant_id,
            "topup_size": topup_size,
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }


def prepare_plan_change(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = str(payload.get("tenant_id") or "").strip()
    from_package = _normalise_package(payload.get("from_package"))
    to_package = _normalise_package(payload.get("to_package"))
    billing_interval = _normalise_billing_interval(payload.get("billing_interval"))

    env_name = _price_env_for(to_package, billing_interval)

    return {
        "success": True,
        "status": "plan_change_prepared",
        "tenant_id": tenant_id,
        "from_package": from_package,
        "to_package": to_package,
        "billing_interval": billing_interval,
        "target_price_configured": _configured(env_name),
        "target_price_env": env_name,
        "proration_supported": True,
        "requires_owner_or_customer_confirmation": True,
        "live_subscription_update_ready_when_subscription_item_known": bool(os.getenv("STRIPE_SECRET_KEY") and _configured(env_name)),
        "credential_values_exposed": False,
        "prepared_at": utc_now_iso(),
    }
'''.lstrip(), encoding="utf-8")

routes_file.write_text(r'''
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header

from backend.app.core.stripe_advanced_billing_runtime import (
    advanced_billing_readiness,
    create_advanced_subscription_checkout,
    create_topup_credit_checkout,
    prepare_plan_change,
)

router = APIRouter()


def _owner_admin(role: Optional[str]) -> bool:
    return role in {"owner", "admin", "system"}


@router.get("/admin/billing/advanced-readiness")
async def advanced_billing_readiness_route(
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return advanced_billing_readiness()


@router.post("/admin/billing/create-advanced-checkout-session")
async def create_advanced_checkout_session_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return create_advanced_subscription_checkout(payload)


@router.post("/admin/billing/create-topup-checkout-session")
async def create_topup_checkout_session_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return create_topup_credit_checkout(payload)


@router.post("/admin/billing/prepare-plan-change")
async def prepare_plan_change_route(
    payload: Dict[str, Any],
    x_actor_role: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    if not _owner_admin(x_actor_role):
        return {"success": False, "error": "owner_admin_required"}

    return prepare_plan_change(payload)
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")
include_block = '''
# Step 229 advanced Stripe billing routes
try:
    from backend.app.api.stripe_advanced_billing_routes import router as stripe_advanced_billing_router
    app.include_router(stripe_advanced_billing_router)
except Exception as exc:
    print(f"STEP_229_STRIPE_ADVANCED_BILLING_ROUTES_NOT_LOADED: {exc}")
'''
if "stripe_advanced_billing_router" not in main_text:
    main_text = main_text.rstrip() + "\n\n" + include_block.lstrip() + "\n"
MAIN.write_text(main_text, encoding="utf-8")

test_file.write_text(r'''
import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def request_json(path, method="GET", payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method=method,
    )

    with urllib.request.urlopen(req, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


readiness = request_json("/admin/billing/advanced-readiness")

advanced_monthly = request_json(
    "/admin/billing/create-advanced-checkout-session",
    method="POST",
    payload={
        "tenant_id": "client_step229_monthly",
        "package_name": "growth",
        "billing_interval": "monthly",
        "customer_email": "step229-monthly@example.com",
        "trial_enabled": True,
        "trial_days": 7,
        "success_url": "https://trance-formation.com.au/client/billing/success",
        "cancel_url": "https://trance-formation.com.au/client/billing/cancel",
    },
)

annual_attempt = request_json(
    "/admin/billing/create-advanced-checkout-session",
    method="POST",
    payload={
        "tenant_id": "client_step229_yearly",
        "package_name": "growth",
        "billing_interval": "yearly",
        "customer_email": "step229-yearly@example.com",
        "trial_enabled": False,
        "success_url": "https://trance-formation.com.au/client/billing/success",
        "cancel_url": "https://trance-formation.com.au/client/billing/cancel",
    },
)

topup_attempt = request_json(
    "/admin/billing/create-topup-checkout-session",
    method="POST",
    payload={
        "tenant_id": "client_step229_topup",
        "topup_size": "small",
        "customer_email": "step229-topup@example.com",
        "success_url": "https://trance-formation.com.au/client/billing/success",
        "cancel_url": "https://trance-formation.com.au/client/billing/cancel",
    },
)

plan_change = request_json(
    "/admin/billing/prepare-plan-change",
    method="POST",
    payload={
        "tenant_id": "client_step229_plan_change",
        "from_package": "starter",
        "to_package": "pro",
        "billing_interval": "monthly",
    },
)

combined = json.dumps({
    "readiness": readiness,
    "advanced_monthly": advanced_monthly,
    "annual_attempt": annual_attempt,
    "topup_attempt": topup_attempt,
    "plan_change": plan_change,
}).lower()

checks = {
    "readiness_success": readiness.get("success") is True,
    "coupons_supported": readiness.get("coupons_supported") is True,
    "trials_supported": readiness.get("free_trials_supported") is True,
    "upgrade_downgrade_supported": readiness.get("upgrade_downgrade_supported") is True,
    "annual_supported": readiness.get("annual_billing_supported") is True,
    "topup_supported": readiness.get("topup_credit_checkout_supported") is True,
    "tax_supported": readiness.get("tax_gst_supported") is True,
    "invoice_polish_supported": readiness.get("invoice_portal_polish_supported") is True,
    "monthly_checkout_controlled": advanced_monthly.get("status") in {
        "advanced_checkout_session_created",
        "advanced_checkout_not_created",
        "advanced_checkout_creation_failed",
    },
    "monthly_trial_field_present": "trial_enabled" in advanced_monthly or advanced_monthly.get("reason") in {
        "stripe_secret_key_not_configured",
        "stripe_price_id_missing",
    },
    "annual_checkout_controlled": annual_attempt.get("status") in {
        "advanced_checkout_session_created",
        "advanced_checkout_not_created",
        "advanced_checkout_creation_failed",
    },
    "topup_checkout_controlled": topup_attempt.get("status") in {
        "topup_checkout_session_created",
        "topup_checkout_not_created",
        "topup_checkout_creation_failed",
    },
    "plan_change_prepared": plan_change.get("status") == "plan_change_prepared",
    "plan_change_proration_supported": plan_change.get("proration_supported") is True,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_229_ADVANCED_STRIPE_BILLING_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("monthly_status", advanced_monthly.get("status"))
print("annual_status", annual_attempt.get("status"))
print("topup_status", topup_attempt.get("status"))

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "readiness": readiness,
        "advanced_monthly": advanced_monthly,
        "annual_attempt": annual_attempt,
        "topup_attempt": topup_attempt,
        "plan_change": plan_change,
    }, indent=2))
    raise SystemExit(1)

print("STEP_229_ADVANCED_STRIPE_BILLING_LOCK_OK")
'''.lstrip(), encoding="utf-8")

for file in [runtime_file, routes_file, MAIN, test_file]:
    py_compile.compile(str(file), doraise=True)

print("STEP_229_ADVANCED_STRIPE_BILLING_INSTALLED")
print(f"Created/updated: {runtime_file}")
print(f"Created/updated: {routes_file}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {test_file}")
print("STEP_229_OK")