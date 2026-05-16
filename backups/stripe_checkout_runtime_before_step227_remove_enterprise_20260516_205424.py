from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


PACKAGE_PRICE_ENV_MAP = {
    "starter": "STRIPE_PRICE_STARTER_MONTHLY",
    "growth": "STRIPE_PRICE_GROWTH_MONTHLY",
    "pro": "STRIPE_PRICE_PRO_MONTHLY",
    "enterprise": "STRIPE_PRICE_ENTERPRISE_MONTHLY",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalise_package(package_name: Optional[str]) -> str:
    value = (package_name or "").strip().lower()
    if value in {"starter", "start"}:
        return "starter"
    if value in {"growth", "grow"}:
        return "growth"
    if value in {"pro", "professional"}:
        return "pro"
    if value in {"enterprise", "full", "full_access"}:
        return "enterprise"
    return value


def get_stripe_checkout_readiness() -> Dict[str, Any]:
    secret_key_present = bool(os.getenv("STRIPE_SECRET_KEY"))
    webhook_secret_present = bool(os.getenv("STRIPE_WEBHOOK_SECRET"))

    package_prices = {}
    missing_prices = []

    for package_name, env_name in PACKAGE_PRICE_ENV_MAP.items():
        value = os.getenv(env_name)
        package_prices[package_name] = {
            "env_name": env_name,
            "configured": bool(value),
            "safe_value": "configured" if value else "missing",
        }
        if not value:
            missing_prices.append(package_name)

    try:
        import stripe  # type: ignore
        stripe_sdk_available = True
    except Exception:
        stripe_sdk_available = False

    ready_for_live_checkout = (
        secret_key_present
        and stripe_sdk_available
        and not missing_prices
    )

    return {
        "success": True,
        "checked_at": utc_now_iso(),
        "stripe_sdk_available": stripe_sdk_available,
        "stripe_secret_key_configured": secret_key_present,
        "stripe_webhook_secret_configured": webhook_secret_present,
        "package_prices": package_prices,
        "missing_price_packages": missing_prices,
        "ready_for_live_checkout": ready_for_live_checkout,
        "credential_values_exposed": False,
    }


def get_price_id_for_package(package_name: str) -> Optional[str]:
    normalised = normalise_package(package_name)
    env_name = PACKAGE_PRICE_ENV_MAP.get(normalised)
    if not env_name:
        return None
    return os.getenv(env_name)


def create_subscription_checkout_session(payload: Dict[str, Any]) -> Dict[str, Any]:
    package_name = normalise_package(payload.get("package_name"))
    tenant_id = str(payload.get("tenant_id") or "").strip()
    customer_email = str(payload.get("customer_email") or "").strip()
    success_url = str(payload.get("success_url") or os.getenv("STRIPE_CHECKOUT_SUCCESS_URL") or "").strip()
    cancel_url = str(payload.get("cancel_url") or os.getenv("STRIPE_CHECKOUT_CANCEL_URL") or "").strip()
    client_reference_id = str(payload.get("client_reference_id") or tenant_id or "").strip()

    readiness = get_stripe_checkout_readiness()

    if not tenant_id:
        return {
            "success": False,
            "status": "checkout_not_created",
            "reason": "tenant_id_required",
            "credential_values_exposed": False,
        }

    if not customer_email:
        return {
            "success": False,
            "status": "checkout_not_created",
            "reason": "customer_email_required",
            "credential_values_exposed": False,
        }

    if package_name not in PACKAGE_PRICE_ENV_MAP:
        return {
            "success": False,
            "status": "checkout_not_created",
            "reason": "unknown_package",
            "package_name": package_name,
            "allowed_packages": list(PACKAGE_PRICE_ENV_MAP.keys()),
            "credential_values_exposed": False,
        }

    price_id = get_price_id_for_package(package_name)

    if not price_id:
        return {
            "success": False,
            "status": "checkout_not_created",
            "reason": "stripe_price_id_missing_for_package",
            "package_name": package_name,
            "required_env": PACKAGE_PRICE_ENV_MAP[package_name],
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    if not success_url or not cancel_url:
        return {
            "success": False,
            "status": "checkout_not_created",
            "reason": "success_url_and_cancel_url_required",
            "credential_values_exposed": False,
        }

    if not readiness.get("stripe_secret_key_configured"):
        return {
            "success": False,
            "status": "checkout_not_created",
            "reason": "stripe_secret_key_not_configured",
            "package_name": package_name,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    if not readiness.get("stripe_sdk_available"):
        return {
            "success": False,
            "status": "checkout_not_created",
            "reason": "stripe_sdk_not_installed",
            "package_name": package_name,
            "readiness": readiness,
            "credential_values_exposed": False,
        }

    try:
        import stripe  # type: ignore

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        session = stripe.checkout.Session.create(
            mode="subscription",
            customer_email=customer_email,
            client_reference_id=client_reference_id,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            subscription_data={
                "metadata": {
                    "tenant_id": tenant_id,
                    "package_name": package_name,
                    "billing_model": "automatic_recurring_monthly_subscription",
                    "contract_type": "month_to_month",
                }
            },
            metadata={
                "tenant_id": tenant_id,
                "package_name": package_name,
                "client_reference_id": client_reference_id,
            },
            allow_promotion_codes=True,
        )

        return {
            "success": True,
            "status": "checkout_session_created",
            "tenant_id": tenant_id,
            "package_name": package_name,
            "stripe_checkout_session_id": getattr(session, "id", None),
            "checkout_url": getattr(session, "url", None),
            "mode": "subscription",
            "billing_model": "automatic_recurring_monthly_subscription",
            "contract_type": "month_to_month",
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": "checkout_creation_failed",
            "reason": type(exc).__name__,
            "safe_message": str(exc),
            "tenant_id": tenant_id,
            "package_name": package_name,
            "credential_values_exposed": False,
            "created_at": utc_now_iso(),
        }
