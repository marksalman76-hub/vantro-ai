from __future__ import annotations

from typing import Any, Dict

from backend.app.core.global_agent_registry import global_agent_registry_summary
from backend.app.core.stripe_production_hardening_runtime import stripe_production_env_readiness
from backend.app.core.live_stripe_bridge_runtime import live_stripe_bridge_readiness
from backend.app.core.marketplace_commercial_bridge import package_pricing_catalogue
from backend.app.core.saas_provisioning_runtime import provisioning_readiness


def final_deployment_readiness() -> Dict[str, Any]:
    agents = global_agent_registry_summary()
    stripe_env = stripe_production_env_readiness()
    live_stripe = live_stripe_bridge_readiness()
    pricing = package_pricing_catalogue()
    provisioning = provisioning_readiness()

    checks = {
        "agent_registry_27_ready": agents.get("agent_count") == 27,
        "all_agents_purchasable": agents.get("purchasable_count") == 27,
        "stripe_env_ready": stripe_env.get("production_ready") is True,
        "live_stripe_ready": live_stripe.get("live_stripe_ready") is True,
        "pricing_ready": pricing.get("success") is True,
        "provisioning_ready": provisioning.get("success") is True,
        "enterprise_contact_us": pricing.get("packages", {}).get("enterprise", {}).get("contact_us_required") is True,
        "secret_exposure": False,
    }

    launch_ready = all(value is True for key, value in checks.items() if key != "secret_exposure")

    return {
        "success": True,
        "deployment_profile": "priority11_final_enterprise_deployment_readiness_v1",
        "launch_ready": launch_ready,
        "checks": checks,
        "agent_registry": {
            "agent_count": agents.get("agent_count"),
            "registry_profile": agents.get("registry_profile"),
        },
        "billing": {
            "production_ready": stripe_env.get("production_ready"),
            "live_stripe_ready": live_stripe.get("live_stripe_ready"),
            "missing_keys": stripe_env.get("missing_keys", []),
            "missing_price_keys": live_stripe.get("missing_price_keys", []),
        },
        "packages": pricing.get("packages"),
        "provisioning": {
            "tenant_provisioning_enabled": provisioning.get("tenant_provisioning_enabled"),
            "one_time_secure_deployment_links_enabled": provisioning.get("one_time_secure_deployment_links_enabled"),
            "client_access_limited_to_paid_agents": provisioning.get("client_access_limited_to_paid_agents"),
        },
        "customer_safe_response_mode": True,
        "secret_exposure": False,
    }
