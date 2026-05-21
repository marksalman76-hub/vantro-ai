from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

FILES = [
    ROOT / "backend" / "app" / "core" / "marketplace_entitlement_runtime.py",
    ROOT / "backend" / "app" / "core" / "marketplace_activation_runtime.py",
    ROOT / "backend" / "app" / "core" / "marketplace_commercial_bridge.py",
    ROOT / "backend" / "app" / "core" / "billing_automation_runtime.py",
    ROOT / "backend" / "app" / "core" / "stripe_production_hardening_runtime.py",
    ROOT / "backend" / "app" / "core" / "live_stripe_bridge_runtime.py",
    ROOT / "backend" / "app" / "core" / "global_agent_registry.py",
]

for path in FILES:
    if path.exists():
        backup = BACKUP_DIR / f"{path.name}_before_real_subscription_rules_{timestamp}"
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

# 1) Marketplace entitlement limits
p = ROOT / "backend" / "app" / "core" / "marketplace_entitlement_runtime.py"
s = p.read_text(encoding="utf-8")
s = s.replace('"starter": 2,\n    "growth": 5,\n    "business": 10,\n    "enterprise": 999,', '"starter": 1,\n    "growth": 3,\n    "business": 5,\n    "enterprise": 999,')
p.write_text(s, encoding="utf-8")

# 2) Commercial pricing bridge: USD prices and Enterprise contact-us
p = ROOT / "backend" / "app" / "core" / "marketplace_commercial_bridge.py"
s = p.read_text(encoding="utf-8")
start = s.find("PACKAGE_PRICING = {")
end = s.find("\n\n\ndef _now()", start)
if start == -1 or end == -1:
    raise RuntimeError("Could not locate PACKAGE_PRICING block")

new_pricing = '''PACKAGE_PRICING = {
    "starter": {
        "monthly_usd": 99,
        "agent_limit": 1,
        "positioning": "Starter automation package",
        "stripe_checkout_enabled": True,
    },
    "growth": {
        "monthly_usd": 279,
        "agent_limit": 3,
        "positioning": "Growth automation package",
        "stripe_checkout_enabled": True,
    },
    "business": {
        "monthly_usd": 399,
        "agent_limit": 5,
        "positioning": "Business automation package",
        "stripe_checkout_enabled": True,
    },
    "enterprise": {
        "monthly_usd": None,
        "agent_limit": 999,
        "positioning": "Custom enterprise automation package",
        "stripe_checkout_enabled": False,
        "contact_us_required": True,
        "unique_price_link_after_owner_discussion": True,
    },
}'''
s = s[:start] + new_pricing + s[end:]

s = s.replace('"currency": "AUD"', '"currency": "USD"')
s = s.replace('"current_monthly_aud"', '"current_monthly_usd"')
s = s.replace('"target_monthly_aud"', '"target_monthly_usd"')
s = s.replace('"monthly_delta_aud"', '"monthly_delta_usd"')
s = s.replace('current_price = PACKAGE_PRICING[current_package]["monthly_aud"]', 'current_price = PACKAGE_PRICING[current_package]["monthly_usd"]')
s = s.replace('target_price = PACKAGE_PRICING[target_package]["monthly_aud"]', 'target_price = PACKAGE_PRICING[target_package]["monthly_usd"]')
p.write_text(s, encoding="utf-8")

# 3) Billing automation: USD-safe checkout payload
p = ROOT / "backend" / "app" / "core" / "billing_automation_runtime.py"
s = p.read_text(encoding="utf-8")
s = s.replace('"currency": "AUD"', '"currency": "USD"')
s = s.replace('"monthly_amount_aud": pricing["monthly_aud"]', '"monthly_amount_usd": pricing["monthly_usd"]')
p.write_text(s, encoding="utf-8")

# 4) Enterprise-only agents in global registry
p = ROOT / "backend" / "app" / "core" / "global_agent_registry.py"
s = p.read_text(encoding="utf-8")
s = s.replace('"agent_id": "head_agent",\n        "name": "Head Agent / CEO",', '"agent_id": "head_agent",\n        "name": "Head Agent / CEO",\n        "enterprise_only": True,')
s = s.replace('"agent_id": "orchestration_agent",\n        "name": "Orchestration Agent",', '"agent_id": "orchestration_agent",\n        "name": "Orchestration Agent",\n        "enterprise_only": True,')
p.write_text(s, encoding="utf-8")

# 5) Enforce enterprise-only in marketplace entitlement runtime
p = ROOT / "backend" / "app" / "core" / "marketplace_entitlement_runtime.py"
s = p.read_text(encoding="utf-8")
old = '''        purchased = agent_id in purchased_agents
        active = agent_id in active_agents

        available_to_activate = (
            purchased
            and not active
            and (active_count < package_limit or package == "enterprise")
        )

        locked_reason = None
        if not purchased:
            locked_reason = "not_purchased"
        elif not active and not available_to_activate:
            locked_reason = "package_limit_reached"
'''
new = '''        enterprise_only = bool(agent.get("enterprise_only"))
        purchased = agent_id in purchased_agents
        active = agent_id in active_agents

        locked_reason = None
        if enterprise_only and package != "enterprise":
            purchased = False
            active = False
            locked_reason = "enterprise_only"
        elif not purchased:
            locked_reason = "not_purchased"

        available_to_activate = (
            purchased
            and not active
            and (active_count < package_limit or package == "enterprise")
            and locked_reason is None
        )

        if purchased and not active and not available_to_activate and locked_reason is None:
            locked_reason = "package_limit_reached"
'''
if old not in s:
    raise RuntimeError("Could not patch marketplace entitlement lock logic")
s = s.replace(old, new)
s = s.replace('"locked": not purchased or locked_reason == "package_limit_reached"', '"locked": locked_reason is not None')
s = s.replace('"requires_owner_approval_for_high_risk": agent.get("requires_owner_approval_for_high_risk", True),', '"requires_owner_approval_for_high_risk": agent.get("requires_owner_approval_for_high_risk", True),\n            "enterprise_only": bool(agent.get("enterprise_only")),')
p.write_text(s, encoding="utf-8")

# 6) Enforce enterprise-only in activation runtime
p = ROOT / "backend" / "app" / "core" / "marketplace_activation_runtime.py"
s = p.read_text(encoding="utf-8")
needle = '''    if not agent:
        return {"success": False, "error": "unknown_agent", "agent_id": agent_id}

    if agent_id not in purchased_agents:
'''
insert = '''    if not agent:
        return {"success": False, "error": "unknown_agent", "agent_id": agent_id}

    if bool(agent.get("enterprise_only")) and package != "enterprise":
        return {
            "success": False,
            "error": "enterprise_only_agent",
            "agent_id": agent_id,
            "upgrade_required": True,
            "enterprise_contact_required": True,
            "customer_safe_message": "This agent is available on Enterprise after owner review.",
        }

    if agent_id not in purchased_agents:
'''
if needle not in s:
    raise RuntimeError("Could not patch activation enterprise-only logic")
s = s.replace(needle, insert)
p.write_text(s, encoding="utf-8")

# 7) Live Stripe env mapping remains Starter/Growth/Business only
p = ROOT / "backend" / "app" / "core" / "live_stripe_bridge_runtime.py"
s = p.read_text(encoding="utf-8")
s = s.replace('"business": "STRIPE_PRICE_BUSINESS_MONTHLY",\n    "enterprise": "STRIPE_PRICE_ENTERPRISE_MONTHLY",', '"business": "STRIPE_PRICE_BUSINESS_MONTHLY",')
p.write_text(s, encoding="utf-8")

# 8) Stripe hardening readiness should not require enterprise
p = ROOT / "backend" / "app" / "core" / "stripe_production_hardening_runtime.py"
s = p.read_text(encoding="utf-8")
s = s.replace('"STRIPE_PRICE_BUSINESS_MONTHLY",\n    "STRIPE_PRICE_ENTERPRISE_MONTHLY",', '"STRIPE_PRICE_BUSINESS_MONTHLY",')
p.write_text(s, encoding="utf-8")

TEST = ROOT / "test_priority10_real_subscription_package_rules.py"
TEST.write_text(r'''
import json
import requests

BASE = "http://127.0.0.1:8000"
HEADERS = {
    "x-actor-role": "admin",
    "x-tenant-id": "owner",
    "Content-Type": "application/json",
}

def show(label, response):
    print("\n" + "=" * 80)
    print(label)
    print("HTTP", response.status_code)
    print(json.dumps(response.json(), indent=2)[:12000])

pricing = requests.get(f"{BASE}/client/marketplace/pricing", headers=HEADERS, timeout=30)
show("PRICING", pricing)

workspace = requests.post(
    f"{BASE}/client/marketplace/workspace",
    headers=HEADERS,
    json={
        "tenant_id": "tenant_real_rules",
        "client_number": "CL-REAL-RULES",
        "package": "business",
        "purchased_agents": [
            "marketing_specialist_agent",
            "crm_ai_agent",
            "ugc_creative_agent",
            "product_image_agent",
            "seo_agent",
            "head_agent",
            "orchestration_agent"
        ],
        "active_agents": [
            "marketing_specialist_agent",
            "crm_ai_agent",
            "ugc_creative_agent"
        ]
    },
    timeout=30,
)
show("BUSINESS_WORKSPACE", workspace)

activate_head = requests.post(
    f"{BASE}/admin/marketplace/activate-agent",
    headers=HEADERS,
    json={
        "tenant_id": "tenant_real_rules",
        "package": "business",
        "purchased_agents": ["head_agent"],
        "active_agents": [],
        "agent_id": "head_agent",
    },
    timeout=30,
)
show("BLOCK_HEAD_AGENT_ON_BUSINESS", activate_head)

enterprise_head = requests.post(
    f"{BASE}/admin/marketplace/activate-agent",
    headers=HEADERS,
    json={
        "tenant_id": "tenant_real_rules_enterprise",
        "package": "enterprise",
        "purchased_agents": ["head_agent"],
        "active_agents": [],
        "agent_id": "head_agent",
    },
    timeout=30,
)
show("ALLOW_HEAD_AGENT_ON_ENTERPRISE", enterprise_head)

checkout = requests.post(
    f"{BASE}/billing/checkout-session-payload",
    headers=HEADERS,
    json={
        "tenant_id": "tenant_real_rules_checkout",
        "client_number": "CL-REAL-CHECKOUT",
        "customer_email": "sale@protekepoxy.com.au",
        "target_package": "business",
        "purchased_agents": ["marketing_specialist_agent"],
        "active_agents": ["marketing_specialist_agent"],
    },
    timeout=30,
)
show("BUSINESS_CHECKOUT_PAYLOAD", checkout)

pricing_json = pricing.json()
workspace_json = workspace.json()
activate_head_json = activate_head.json()
enterprise_head_json = enterprise_head.json()
checkout_json = checkout.json()

assert pricing_json["success"] is True
assert pricing_json["currency"] == "USD"
assert pricing_json["packages"]["starter"]["monthly_usd"] == 99
assert pricing_json["packages"]["starter"]["agent_limit"] == 1
assert pricing_json["packages"]["growth"]["monthly_usd"] == 279
assert pricing_json["packages"]["growth"]["agent_limit"] == 3
assert pricing_json["packages"]["business"]["monthly_usd"] == 399
assert pricing_json["packages"]["business"]["agent_limit"] == 5
assert pricing_json["packages"]["enterprise"]["monthly_usd"] is None
assert pricing_json["packages"]["enterprise"]["contact_us_required"] is True

assert workspace_json["success"] is True
assert workspace_json["package_limit"] == 5
catalogue = []
for items in workspace_json["marketplace_by_category"].values():
    catalogue.extend(items)

head = next(a for a in catalogue if a["agent_id"] == "head_agent")
orch = next(a for a in catalogue if a["agent_id"] == "orchestration_agent")
assert head["locked"] is True
assert head["locked_reason"] == "enterprise_only"
assert orch["locked"] is True
assert orch["locked_reason"] == "enterprise_only"

assert activate_head_json["success"] is False
assert activate_head_json["error"] == "enterprise_only_agent"

assert enterprise_head_json["success"] is True
assert enterprise_head_json["status"] == "agent_activated"

assert checkout_json["success"] is True
assert checkout_json["currency"] == "USD"
assert checkout_json["monthly_amount_usd"] == 399
assert checkout_json["target_package"] == "business"

print("\nPRIORITY10_REAL_SUBSCRIPTION_PACKAGE_RULES_OK")
'''.lstrip(), encoding="utf-8")

print("PRIORITY10_REAL_SUBSCRIPTION_PACKAGE_RULES_FIXED")
print("Starter=$99 USD / 1 agent")
print("Growth=$279 USD / 3 agents")
print("Business=$399 USD / 5 agents")
print("Enterprise=Contact us / custom")
print("Head Agent and Orchestration Agent are Enterprise-only")