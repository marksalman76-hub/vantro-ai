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
