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
    "client_name": "Priority 8 Workspace Bootstrap Test Client",
    "client_email": "sale@protekepoxy.com.au",
    "package_id": "growth",
    "billing_status": "paid",
    "payment_reference": "priority8-workspace-bootstrap-test-payment-001",
    "selected_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent"
    ],
    "country": "Australia",
    "region": "NSW",
    "currency": "AUD",
    "source": "priority8_workspace_bootstrap_test"
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
client_number = tenant.get("client_number")
token = extract_token(provision_json.get("one_time_activation_url"))

assert provision.status_code == 200
assert provision_json.get("success") is True
assert tenant_id
assert client_number
assert token

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
show("VALIDATE_AND_CONSUME_LINK", validate)

assert validate.status_code == 200
assert validate.json().get("success") is True
assert validate.json().get("used") is True

retrieve_by_tenant = requests.post(
    f"{BASE}/admin/saas-provisioning/tenant-bootstrap",
    headers=HEADERS,
    json={"tenant_id": tenant_id},
    timeout=30,
)
show("RETRIEVE_BY_TENANT_ID", retrieve_by_tenant)

retrieve_by_client_number = requests.post(
    f"{BASE}/admin/saas-provisioning/tenant-bootstrap",
    headers=HEADERS,
    json={"client_number": client_number},
    timeout=30,
)
show("RETRIEVE_BY_CLIENT_NUMBER", retrieve_by_client_number)

for response in [retrieve_by_tenant, retrieve_by_client_number]:
    data = response.json()
    bootstrap = data.get("client_workspace_bootstrap", {})
    links = data.get("deployment_links", [])
    audits = data.get("audit_events", [])

    assert response.status_code == 200
    assert data.get("success") is True
    assert data.get("secret_exposure") is False
    assert data.get("internal_config_hidden_from_client") is True

    assert bootstrap.get("tenant_id") == tenant_id
    assert bootstrap.get("client_number") == client_number
    assert bootstrap.get("package") == "growth"
    assert bootstrap.get("active_agents") == [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent"
    ]
    assert bootstrap.get("client_access_limited_to_paid_agents") is True
    assert bootstrap.get("governance_bypass") is False
    assert bootstrap.get("entitlement_bypass") is False

    assert len(links) >= 1
    assert links[-1].get("used") is True
    assert links[-1].get("blocked_after_use") is True
    assert links[-1].get("token_hash") == "hidden"

    assert len(audits) >= 1

print("\nPRIORITY8_TENANT_WORKSPACE_BOOTSTRAP_LOCK_OK")
