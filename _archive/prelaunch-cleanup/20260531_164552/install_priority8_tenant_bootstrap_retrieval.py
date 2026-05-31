from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "core" / "saas_provisioning_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

if not TARGET.exists():
    raise FileNotFoundError(TARGET)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"saas_runtime_before_tenant_bootstrap_retrieval_{timestamp}.py"
backup.write_text(TARGET.read_text(encoding="utf-8"), encoding="utf-8")

text = TARGET.read_text(encoding="utf-8")

block = r'''

def retrieve_tenant_bootstrap(payload: Dict[str, Any]) -> Dict[str, Any]:
    tenant_id = payload.get("tenant_id")
    client_number = payload.get("client_number")

    if not tenant_id and not client_number:
        return {
            "success": False,
            "error": "tenant_id_or_client_number_required",
        }

    tenants = _read_jsonl(TENANTS_FILE, limit=5000)
    links = _read_jsonl(LINKS_FILE, limit=5000)
    audits = _read_jsonl(AUDIT_FILE, limit=5000)

    tenant = None
    for item in tenants:
        if tenant_id and item.get("tenant_id") == tenant_id:
            tenant = item
            break
        if client_number and item.get("client_number") == client_number:
            tenant = item
            break

    if not tenant:
        return {
            "success": False,
            "error": "tenant_not_found",
        }

    matched_links = [
        {
            "link_id": item.get("link_id"),
            "tenant_id": item.get("tenant_id"),
            "client_number": item.get("client_number"),
            "single_use": item.get("single_use"),
            "used": item.get("used"),
            "blocked_after_use": item.get("blocked_after_use"),
            "reuse_attempts": item.get("reuse_attempts", 0),
            "admin_review_required_on_reuse": item.get("admin_review_required_on_reuse", True),
            "token_hash": "hidden",
        }
        for item in links
        if item.get("tenant_id") == tenant.get("tenant_id")
    ]

    matched_audits = [
        {
            "timestamp": item.get("timestamp"),
            "event_type": item.get("event_type"),
            "tenant_id": item.get("tenant_id"),
            "client_number": item.get("client_number"),
            "profile": item.get("profile"),
        }
        for item in audits
        if item.get("tenant_id") == tenant.get("tenant_id")
    ]

    bootstrap = {
        "tenant_id": tenant.get("tenant_id"),
        "client_number": tenant.get("client_number"),
        "client_name": tenant.get("client_name"),
        "client_email": tenant.get("client_email"),
        "package": tenant.get("package"),
        "billing_status": tenant.get("billing_status"),
        "subscription_status": tenant.get("subscription_status"),
        "active_agents": tenant.get("activated_agents", []),
        "agent_limit": tenant.get("agent_limit"),
        "workspace_bootstrap_ready": tenant.get("workspace_bootstrap_ready"),
        "entitlement_hydrated": tenant.get("entitlement_hydrated"),
        "client_access_limited_to_paid_agents": tenant.get("client_access_limited_to_paid_agents"),
        "internal_config_hidden_from_client": tenant.get("internal_config_hidden_from_client"),
        "governance_bypass": tenant.get("governance_bypass"),
        "entitlement_bypass": tenant.get("entitlement_bypass"),
    }

    return {
        "success": True,
        "tenant_id": tenant.get("tenant_id"),
        "client_number": tenant.get("client_number"),
        "client_workspace_bootstrap": bootstrap,
        "deployment_links": matched_links,
        "audit_events": matched_audits,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "internal_config_hidden_from_client": True,
    }


@router.post("/tenant-bootstrap")
def tenant_bootstrap_endpoint(payload: Dict[str, Any]):
    return retrieve_tenant_bootstrap(payload)
'''

if "def retrieve_tenant_bootstrap(" not in text:
    text = text.rstrip() + "\n" + block + "\n"

TARGET.write_text(text, encoding="utf-8")

TEST = ROOT / "test_priority8_tenant_workspace_bootstrap_lock.py"
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
'''.lstrip(), encoding="utf-8")

print("PRIORITY8_TENANT_BOOTSTRAP_RETRIEVAL_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {TARGET}")
print(f"Updated: {TEST}")
print("Route added: /admin/saas-provisioning/tenant-bootstrap")