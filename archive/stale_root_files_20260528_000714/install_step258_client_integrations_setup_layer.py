from pathlib import Path
from datetime import datetime
import json
import py_compile

ROOT = Path.cwd()
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs" / "operations"
TEST = ROOT / "test_step258_client_integrations_setup_layer.py"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

record = {
    "success": True,
    "step": 258,
    "status": "client_integrations_setup_layer_locked",
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "usage_modes": {
        "portal_only_mode": {
            "description": "Client can activate, log in, run assigned agents, and generate outputs without connecting external systems.",
            "requires_integrations": False,
        },
        "connected_execution_mode": {
            "description": "Client connects business tools so agents can prepare or execute real workflow actions.",
            "requires_integrations": True,
        },
    },
    "integration_categories": {
        "shopify": {
            "purpose": "Store/product/page execution",
            "required_for": ["product publishing", "store updates", "product catalogue actions"],
            "owner_approval_required_for": ["major theme changes", "bulk product changes"],
        },
        "crm": {
            "purpose": "Lead/customer pipeline execution",
            "examples": ["GoHighLevel", "HubSpot"],
            "owner_approval_required_for": ["bulk contact actions", "deal-stage automation changes"],
        },
        "email_marketing": {
            "purpose": "Campaign sending and automation",
            "examples": ["Brevo", "Mailchimp", "Klaviyo"],
            "owner_approval_required_for": ["live campaign send", "large audience send"],
        },
        "ads": {
            "purpose": "Campaign analysis and ad preparation",
            "examples": ["Meta", "Google Ads", "TikTok Ads"],
            "owner_approval_required_for": ["spend increase", "campaign scaling", "new budget commitment"],
        },
        "analytics": {
            "purpose": "Performance analysis and optimisation",
            "examples": ["GA4", "Search Console", "Shopify Analytics"],
            "owner_approval_required_for": [],
        },
        "support": {
            "purpose": "Customer support drafting and inbox workflows",
            "examples": ["Gmail", "Helpdesk", "Support inbox"],
            "owner_approval_required_for": ["bulk replies", "refund/financial actions"],
        },
    },
    "onboarding_flow": [
        "Client activates account.",
        "Client logs in.",
        "Client completes business profile.",
        "Client connects required integrations.",
        "Client confirms permitted automation actions.",
        "Agents run in portal-only or connected execution mode.",
        "High-risk actions continue through owner approval gates.",
    ],
}

record_file = DATA / "step258_client_integrations_setup_layer.json"
record_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

(DOCS / "client-integrations-setup.md").write_text("""# Client Integrations Setup

## Modes

### Portal-only mode
The client can use assigned agents immediately after activation/login to create outputs, plans, copy, briefs, recommendations, and reports.

### Connected execution mode
To execute actions inside the client’s business systems, integrations must be connected.

## Required Integration Areas

1. Shopify / ecommerce store
2. CRM
3. Email marketing
4. Ads platforms
5. Analytics
6. Support inbox/helpdesk

## Governance

The system may prepare actions automatically, but owner approval remains required for:
- advertising spend increases
- campaign scaling
- major website/store changes
- bulk sends
- paid influencer commitments
- refunds or financial actions
- subscription/package changes

## Client Onboarding

Client activates account → logs in → completes business profile → connects tools → confirms permissions → runs agents.
""", encoding="utf-8")

TEST.write_text(r'''
import json
from pathlib import Path

ROOT = Path.cwd()
record = json.loads((ROOT / "backend" / "app" / "data" / "step258_client_integrations_setup_layer.json").read_text(encoding="utf-8"))
doc = ROOT / "docs" / "operations" / "client-integrations-setup.md"

required = ["shopify", "crm", "email_marketing", "ads", "analytics", "support"]

checks = {
    "record_success": record.get("success") is True,
    "status_locked": record.get("status") == "client_integrations_setup_layer_locked",
    "portal_only_mode_present": "portal_only_mode" in record.get("usage_modes", {}),
    "connected_execution_mode_present": "connected_execution_mode" in record.get("usage_modes", {}),
    "all_integration_categories_present": all(key in record.get("integration_categories", {}) for key in required),
    "onboarding_flow_present": len(record.get("onboarding_flow", [])) >= 6,
    "setup_doc_created": doc.exists(),
}

print("STEP_258_CLIENT_INTEGRATIONS_SETUP_LAYER_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]
if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_258_CLIENT_INTEGRATIONS_SETUP_LAYER_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_258_CLIENT_INTEGRATIONS_SETUP_LAYER_INSTALLED")
print(f"Created/updated: {record_file}")
print(f"Created/updated: {DOCS / 'client-integrations-setup.md'}")
print(f"Created/updated: {TEST}")
print("STEP_258_OK")