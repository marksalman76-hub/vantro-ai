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
        print(json.dumps(response.json(), indent=2)[:7000])
    except Exception:
        print(response.text[:7000])

def extract_token(value):
    if not value:
        return None
    match = re.search(r"token=([^&]+)", value)
    return match.group(1) if match else value

payload = {
    "client_name": "Priority 8 Single Use Test Client",
    "client_email": "sale@protekepoxy.com.au",
    "package_id": "growth",
    "billing_status": "paid",
    "payment_reference": "priority8-single-use-test-payment-001",
    "selected_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent"
    ],
    "country": "Australia",
    "region": "NSW",
    "currency": "AUD",
    "source": "priority8_single_use_activation_test"
}

provision = requests.post(
    f"{BASE}/admin/saas-provisioning/provision-tenant",
    headers=HEADERS,
    json=payload,
    timeout=30,
)
show("PROVISION_TENANT", provision)

provision_json = provision.json()
tenant = provision_json.get("tenant", {})
tenant_id = tenant.get("tenant_id")
activation_url = provision_json.get("one_time_activation_url")
token = extract_token(activation_url)

print("\nTENANT_ID", tenant_id)
print("ACTIVATION_URL", activation_url)
print("TOKEN", token)

assert provision.status_code == 200, "provision route failed"
assert provision_json.get("success") is True, "provision failed"
assert tenant_id, "tenant_id missing"
assert token, "activation token missing"

first_validate = requests.post(
    f"{BASE}/admin/saas-provisioning/validate-one-time-link",
    headers=HEADERS,
    json={
        "tenant_id": tenant_id,
        "token": token,
        "client_email": "sale@protekepoxy.com.au"
    },
    timeout=30,
)
show("FIRST_VALIDATE", first_validate)

second_validate = requests.post(
    f"{BASE}/admin/saas-provisioning/validate-one-time-link",
    headers=HEADERS,
    json={
        "tenant_id": tenant_id,
        "token": token,
        "client_email": "sale@protekepoxy.com.au"
    },
    timeout=30,
)
show("SECOND_VALIDATE_REUSE_ATTEMPT", second_validate)

first_json = first_validate.json()
second_json = second_validate.json()

assert first_validate.status_code == 200, "first validation HTTP failed"
assert first_json.get("success") is True, f"first validation failed: {first_json}"
assert first_json.get("valid") is True, f"first validation not valid: {first_json}"

assert second_validate.status_code == 200, "second validation HTTP failed"
assert second_json.get("success") is False or second_json.get("valid") is False, (
    f"single-use link reuse was not blocked: {second_json}"
)

print("\nPRIORITY8_SINGLE_USE_ACTIVATION_LOCK_OK")