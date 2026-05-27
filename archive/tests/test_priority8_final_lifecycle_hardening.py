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
