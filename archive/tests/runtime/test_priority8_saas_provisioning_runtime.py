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

def extract_token_from_url(value):
    if not value:
        return None
    match = re.search(r"token=([^&]+)", value)
    return match.group(1) if match else value

readiness = requests.get(
    f"{BASE}/admin/saas-provisioning/readiness",
    headers=HEADERS,
    timeout=30,
)
show("READINESS", readiness)

provision_payload = {
    "client_name": "Priority 8 Test Client",
    "client_email": "sale@protekepoxy.com.au",
    "package_id": "growth",
    "billing_status": "paid",
    "payment_reference": "priority8-test-payment-001",
    "selected_agents": [
        "head_agent",
        "marketing_specialist_agent",
        "crm_ai_agent"
    ],
    "country": "Australia",
    "region": "NSW",
    "currency": "AUD",
    "source": "priority8_runtime_test"
}

provision = requests.post(
    f"{BASE}/admin/saas-provisioning/provision-tenant",
    headers=HEADERS,
    json=provision_payload,
    timeout=30,
)
show("PROVISION_TENANT", provision)

provision_json = provision.json()

tenant = provision_json.get("tenant", {})
link = provision_json.get("one_time_deployment_link", {})

tenant_id = tenant.get("tenant_id") or provision_json.get("tenant_id")
package = tenant.get("package")
activated_agents = tenant.get("activated_agents", [])
requested_agents = tenant.get("requested_agents", [])

activation_url = (
    provision_json.get("one_time_activation_url")
    or link.get("deployment_path")
    or provision_json.get("activation_link")
)

token = (
    provision_json.get("one_time_token")
    or provision_json.get("activation_token")
    or provision_json.get("token")
    or extract_token_from_url(activation_url)
)

print("\nEXTRACTED_TENANT_ID", tenant_id)
print("EXTRACTED_PACKAGE", package)
print("EXTRACTED_REQUESTED_AGENTS", requested_agents)
print("EXTRACTED_ACTIVATED_AGENTS", activated_agents)
print("EXTRACTED_ACTIVATION_URL", activation_url)
print("EXTRACTED_TOKEN", token)

validate_payload = {
    "tenant_id": tenant_id,
    "token": token,
    "client_email": "sale@protekepoxy.com.au"
}

validate = requests.post(
    f"{BASE}/admin/saas-provisioning/validate-one-time-link",
    headers=HEADERS,
    json=validate_payload,
    timeout=30,
)
show("VALIDATE_ONE_TIME_LINK", validate)

validate_json = validate.json()

assert readiness.status_code == 200, "readiness route failed"
assert readiness.json().get("success") is True, "readiness success false"

assert provision.status_code == 200, "provision tenant route failed"
assert provision_json.get("success") is True, "provision success false"

assert tenant_id, "tenant_id missing"
assert package == "growth", f"package alias failed, got {package}"
assert "head_agent" in requested_agents or "head_agent" in activated_agents, "selected_agents alias failed"

assert token, "activation token missing"
assert validate.status_code == 200, "validate one-time link HTTP failed"
assert validate_json.get("success") is True, f"validation failed: {validate_json}"

print("\nPRIORITY8_SAAS_PROVISIONING_RUNTIME_TEST_OK")
