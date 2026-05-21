from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MAIN = ROOT / "backend" / "app" / "main.py"
RUNTIME = ROOT / "backend" / "app" / "core" / "saas_provisioning_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

main_backup = BACKUP_DIR / f"main_before_priority8_final_lifecycle_{timestamp}.py"
runtime_backup = BACKUP_DIR / f"saas_runtime_before_priority8_final_lifecycle_{timestamp}.py"

main_backup.write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")
runtime_backup.write_text(RUNTIME.read_text(encoding="utf-8"), encoding="utf-8")

runtime_text = RUNTIME.read_text(encoding="utf-8")

lifecycle_block = r'''

def update_tenant_lifecycle(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")
    action = str(payload.get("action") or "").strip().lower()

    allowed = {
        "suspend",
        "deactivate",
        "reactivate",
        "cancel_subscription",
        "complete_onboarding",
    }

    if action not in allowed:
        return {"success": False, "error": "unsupported_lifecycle_action"}

    tenants = _read_jsonl(TENANTS_FILE, limit=5000)

    updated = False
    now = _now_iso()

    for tenant in tenants:
        matched = (
            tenant_id and tenant.get("tenant_id") == tenant_id
        ) or (
            client_number and tenant.get("client_number") == client_number
        )

        if not matched:
            continue

        if action == "suspend":
            tenant["tenant_status"] = "suspended"
            tenant["subscription_status"] = "suspended"
            tenant["client_access_suspended"] = True

        elif action == "deactivate":
            tenant["tenant_status"] = "deactivated"
            tenant["subscription_status"] = "deactivated"
            tenant["activated_agents"] = []
            tenant["client_access_suspended"] = True

        elif action == "reactivate":
            tenant["tenant_status"] = "active"
            tenant["subscription_status"] = tenant.get("subscription_status") or "active"
            tenant["client_access_suspended"] = False

        elif action == "cancel_subscription":
            tenant["subscription_status"] = "cancelled"
            tenant["tenant_status"] = "cancelled"
            tenant["activated_agents"] = []
            tenant["client_access_suspended"] = True
            tenant["billing_status"] = "cancelled"

        elif action == "complete_onboarding":
            tenant["onboarding_status"] = "completed"
            tenant["onboarding_completed_at"] = now
            tenant["subscription_status"] = "active"
            tenant["tenant_status"] = "active"

        tenant["lifecycle_updated_at"] = now
        tenant["last_lifecycle_action"] = action
        updated = True

        _append_jsonl(
            AUDIT_FILE,
            {
                "timestamp": now,
                "event_type": "tenant_lifecycle_updated",
                "tenant_id": tenant.get("tenant_id"),
                "client_number": tenant.get("client_number"),
                "action": action,
                "profile": SAAS_PROVISIONING_PROFILE,
            },
        )

        break

    if not updated:
        return {"success": False, "error": "tenant_not_found"}

    _rewrite_jsonl(TENANTS_FILE, tenants)

    return {
        "success": True,
        "action": action,
        "tenant_id": tenant.get("tenant_id"),
        "client_number": tenant.get("client_number"),
        "tenant_status": tenant.get("tenant_status"),
        "subscription_status": tenant.get("subscription_status"),
        "activated_agents": tenant.get("activated_agents", []),
        "client_access_suspended": tenant.get("client_access_suspended", False),
        "customer_safe_response_mode": True,
        "secret_exposure": False,
    }


def cleanup_expired_activation_links(payload: Dict[str, Any]) -> Dict[str, Any]:
    max_age_hours = int(payload.get("max_age_hours") or 72)
    now_dt = datetime.fromisoformat(_now_iso())

    links = _read_jsonl(LINKS_FILE, limit=5000)

    expired_count = 0

    for link in links:
        if link.get("used") is True:
            continue

        created_at = link.get("created_at")
        if not created_at:
            continue

        try:
            created_dt = datetime.fromisoformat(created_at)
        except Exception:
            continue

        age_hours = (now_dt - created_dt).total_seconds() / 3600

        if age_hours >= max_age_hours:
            link["expired"] = True
            link["expired_at"] = _now_iso()
            link["blocked_after_expiry"] = True
            expired_count += 1

            _append_jsonl(
                AUDIT_FILE,
                {
                    "timestamp": _now_iso(),
                    "event_type": "one_time_link_expired",
                    "tenant_id": link.get("tenant_id"),
                    "client_number": link.get("client_number"),
                    "link_id": link.get("link_id"),
                    "profile": SAAS_PROVISIONING_PROFILE,
                },
            )

    _rewrite_jsonl(LINKS_FILE, links)

    return {
        "success": True,
        "expired_count": expired_count,
        "max_age_hours": max_age_hours,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
    }
'''

if "def update_tenant_lifecycle(" not in runtime_text:
    runtime_text = runtime_text.rstrip() + "\n" + lifecycle_block + "\n"

RUNTIME.write_text(runtime_text, encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

old_import = "from backend.app.core.saas_provisioning_runtime import provisioning_readiness, provision_tenant, validate_one_time_link, retrieve_tenant_bootstrap"
new_import = "from backend.app.core.saas_provisioning_runtime import provisioning_readiness, provision_tenant, validate_one_time_link, retrieve_tenant_bootstrap, update_tenant_lifecycle, cleanup_expired_activation_links"

if old_import in main_text:
    main_text = main_text.replace(old_import, new_import)
elif "update_tenant_lifecycle" not in main_text:
    raise RuntimeError("Could not safely update saas provisioning import in main.py")

routes = r'''

@app.post("/admin/saas-provisioning/tenant-lifecycle")
def admin_saas_provisioning_tenant_lifecycle(payload: dict):
    return update_tenant_lifecycle(payload)


@app.post("/admin/saas-provisioning/cleanup-expired-links")
def admin_saas_provisioning_cleanup_expired_links(payload: dict):
    return cleanup_expired_activation_links(payload)
'''

if "/admin/saas-provisioning/tenant-lifecycle" not in main_text:
    main_text = main_text.rstrip() + "\n" + routes + "\n"

MAIN.write_text(main_text, encoding="utf-8")

TEST = ROOT / "test_priority8_final_lifecycle_hardening.py"
TEST.write_text(r'''
import json
import re
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
    try:
        print(json.dumps(response.json(), indent=2)[:9000])
    except Exception:
        print(response.text[:9000])

def extract_token(value):
    if not value:
        return None
    match = re.search(r"token=([^&]+)", value)
    return match.group(1) if match else value

payload = {
    "client_name": "Priority 8 Final Lifecycle Test Client",
    "client_email": "sale@protekepoxy.com.au",
    "package_id": "growth",
    "billing_status": "paid",
    "payment_reference": "priority8-final-lifecycle-payment-001",
    "selected_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent"
    ],
    "country": "Australia",
    "region": "NSW",
    "currency": "AUD",
    "source": "priority8_final_lifecycle_test"
}

provision = requests.post(
    f"{BASE}/admin/saas-provisioning/provision-tenant",
    headers=HEADERS,
    json=payload,
    timeout=30,
)
show("PROVISION_TENANT", provision)

data = provision.json()
tenant = data["tenant"]
tenant_id = tenant["tenant_id"]
client_number = tenant["client_number"]
token = extract_token(data["one_time_activation_url"])

validate = requests.post(
    f"{BASE}/admin/saas-provisioning/validate-one-time-link",
    headers=HEADERS,
    json={
        "tenant_id": tenant_id,
        "token": token,
        "client_email": "sale@protekepoxy.com.au"
    },
    timeout=30,
)
show("VALIDATE_LINK", validate)

complete = requests.post(
    f"{BASE}/admin/saas-provisioning/tenant-lifecycle",
    headers=HEADERS,
    json={"tenant_id": tenant_id, "action": "complete_onboarding"},
    timeout=30,
)
show("COMPLETE_ONBOARDING", complete)

retrieve_active = requests.post(
    f"{BASE}/admin/saas-provisioning/tenant-bootstrap",
    headers=HEADERS,
    json={"tenant_id": tenant_id},
    timeout=30,
)
show("RETRIEVE_ACTIVE_BOOTSTRAP", retrieve_active)

suspend = requests.post(
    f"{BASE}/admin/saas-provisioning/tenant-lifecycle",
    headers=HEADERS,
    json={"client_number": client_number, "action": "suspend"},
    timeout=30,
)
show("SUSPEND_TENANT", suspend)

cancel = requests.post(
    f"{BASE}/admin/saas-provisioning/tenant-lifecycle",
    headers=HEADERS,
    json={"tenant_id": tenant_id, "action": "cancel_subscription"},
    timeout=30,
)
show("CANCEL_SUBSCRIPTION", cancel)

cleanup = requests.post(
    f"{BASE}/admin/saas-provisioning/cleanup-expired-links",
    headers=HEADERS,
    json={"max_age_hours": 72},
    timeout=30,
)
show("CLEANUP_EXPIRED_LINKS", cleanup)

for response in [provision, validate, complete, retrieve_active, suspend, cancel, cleanup]:
    assert response.status_code == 200

assert provision.json()["success"] is True
assert validate.json()["success"] is True
assert validate.json()["used"] is True

assert complete.json()["success"] is True
assert complete.json()["tenant_status"] == "active"
assert complete.json()["subscription_status"] == "active"

active_bootstrap = retrieve_active.json()["client_workspace_bootstrap"]
assert active_bootstrap["tenant_id"] == tenant_id
assert active_bootstrap["package"] == "growth"
assert active_bootstrap["active_agents"] == [
    "head_agent",
    "marketing_specialist_agent",
    "crm_ai_agent"
]

assert suspend.json()["success"] is True
assert suspend.json()["tenant_status"] == "suspended"
assert suspend.json()["client_access_suspended"] is True

assert cancel.json()["success"] is True
assert cancel.json()["subscription_status"] == "cancelled"
assert cancel.json()["activated_agents"] == []
assert cancel.json()["client_access_suspended"] is True

assert cleanup.json()["success"] is True
assert cleanup.json()["secret_exposure"] is False

print("\nPRIORITY8_FINAL_LIFECYCLE_HARDENING_OK")
'''.lstrip(), encoding="utf-8")

print("PRIORITY8_FINAL_LIFECYCLE_HARDENING_INSTALLED")
print(f"Main backup: {main_backup}")
print(f"Runtime backup: {runtime_backup}")
print(f"Updated: {MAIN}")
print(f"Updated: {RUNTIME}")
print(f"Updated: {TEST}")