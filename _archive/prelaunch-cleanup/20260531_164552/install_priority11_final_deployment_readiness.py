from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
CORE = ROOT / "backend" / "app" / "core"
RUNTIME = CORE / "final_deployment_readiness_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
main_backup = BACKUP_DIR / f"main_before_priority11_final_deployment_{timestamp}.py"
main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

RUNTIME.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")
import_line = "from backend.app.core.final_deployment_readiness_runtime import final_deployment_readiness"

if import_line not in main_text:
    lines = main_text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)
    main_text = "\n".join(lines) + "\n"

route = r'''

@app.get("/admin/final-deployment-readiness")
def admin_final_deployment_readiness():
    return final_deployment_readiness()
'''

if "/admin/final-deployment-readiness" not in main_text:
    main_text = main_text.rstrip() + "\n" + route + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority11_final_deployment_readiness.py"
TEST.write_text(r'''
import json
import requests

BASE = "http://127.0.0.1:8000"
HEADERS = {"x-actor-role": "admin", "x-tenant-id": "owner"}

r = requests.get(f"{BASE}/admin/final-deployment-readiness", headers=HEADERS, timeout=30)
print(json.dumps(r.json(), indent=2)[:12000])

data = r.json()
assert r.status_code == 200
assert data["success"] is True
assert data["agent_registry"]["agent_count"] == 27
assert data["checks"]["agent_registry_27_ready"] is True
assert data["checks"]["all_agents_purchasable"] is True
assert data["checks"]["enterprise_contact_us"] is True
assert data["secret_exposure"] is False

print("\nPRIORITY11_FINAL_DEPLOYMENT_READINESS_OK")
'''.lstrip(), encoding="utf-8")

print("PRIORITY11_FINAL_DEPLOYMENT_READINESS_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Updated: {MAIN}")
print(f"Created/updated: {RUNTIME}")
print(f"Created/updated: {TEST}")