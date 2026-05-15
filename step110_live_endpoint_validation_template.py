from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

validation_template = {
    "step": 110,
    "name": "Live Endpoint Validation Script Template",
    "generated_at_utc": now,
    "status": "live_endpoint_validation_template_created",
    "purpose": "Validate production frontend/backend availability after deployment.",
    "required_live_values": {
        "BACKEND_URL": "",
        "FRONTEND_URL": "",
    },
    "validation_targets": [
        {
            "name": "backend_health",
            "path": "/health",
            "expected": "200 OK",
            "status": "pending_live_url",
        },
        {
            "name": "frontend_homepage",
            "path": "/",
            "expected": "200 OK",
            "status": "pending_live_url",
        },
        {
            "name": "admin_dashboard",
            "path": "/admin",
            "expected": "accessible",
            "status": "pending_live_url",
        },
        {
            "name": "client_portal",
            "path": "/client",
            "expected": "accessible",
            "status": "pending_live_url",
        },
    ],
    "release_decision": {
        "can_continue": True,
        "next_step": "live_provider_configuration_and_real_deployment_validation",
    },
}

json_path = DATA / "step110_live_endpoint_validation_template.json"
md_path = DOCS / "STEP_110_LIVE_ENDPOINT_VALIDATION_TEMPLATE.md"

json_path.write_text(json.dumps(validation_template, indent=2), encoding="utf-8")

rows = "\n".join(
    f"| {item['name']} | {item['path']} | {item['expected']} | {item['status']} |"
    for item in validation_template["validation_targets"]
)

md = f"""# Step 110 — Live Endpoint Validation Template

Generated: {now}

## Status

**Result:** Live endpoint validation template created.

## Required Live Values

- `BACKEND_URL`
- `FRONTEND_URL`

## Validation Targets

| Target | Path | Expected Result | Status |
|---|---|---|---|
{rows}

## Validation Purpose

This template prepares the final live deployment verification stage.

After deployment, validate:

1. Backend `/health`
2. Frontend homepage
3. Admin dashboard route
4. Client portal route
5. HTTPS/TLS access
6. Frontend-to-backend communication
7. CORS compatibility
8. Production runtime stability

## Release Decision

- Can continue: `True`
- Next step: Live provider configuration and real deployment validation.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_110_LIVE_ENDPOINT_VALIDATION_TEMPLATE_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("status", validation_template["status"])
print("can_continue", validation_template["release_decision"]["can_continue"])
print("STEP_110_OK")