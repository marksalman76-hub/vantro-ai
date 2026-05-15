from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

required_paths = [
    "backend",
    "docs",
    "backend/app",
    "backend/app/data",
    "backend/app/core",
]

optional_paths = [
    "frontend",
    "apps/web",
    "tests",
    "scripts",
    "backups",
]

required_docs = [
    "docs/STEP_101_PRODUCTION_DEPLOYMENT_CHECKLIST_RELEASE_LOCK.md",
    "docs/STEP_102_PRODUCTION_ENVIRONMENT_VARIABLE_AUDIT.md",
    "docs/PRODUCTION_ENVIRONMENT_TEMPLATE_DO_NOT_COMMIT_SECRETS.env",
    "docs/STEP_104_PRODUCTION_ENDPOINT_DOMAIN_READINESS.md",
]

required_data_records = [
    "backend/app/data/step101_production_release_lock.json",
    "backend/app/data/step102_production_env_audit.json",
    "backend/app/data/step103_production_env_template_record.json",
    "backend/app/data/step104_production_endpoint_readiness.json",
]

audit = {
    "step": 105,
    "name": "Local Production Release Bundle Audit",
    "generated_at_utc": now,
    "project_root": str(ROOT),
    "required_paths": {},
    "optional_paths": {},
    "required_docs": {},
    "required_data_records": {},
    "release_bundle_status": "pending",
}

for item in required_paths:
    audit["required_paths"][item] = (ROOT / item).exists()

for item in optional_paths:
    audit["optional_paths"][item] = (ROOT / item).exists()

for item in required_docs:
    audit["required_docs"][item] = (ROOT / item).exists()

for item in required_data_records:
    audit["required_data_records"][item] = (ROOT / item).exists()

required_ok = all(audit["required_paths"].values())
docs_ok = all(audit["required_docs"].values())
records_ok = all(audit["required_data_records"].values())

audit["release_bundle_status"] = (
    "local_release_bundle_ready"
    if required_ok and docs_ok and records_ok
    else "local_release_bundle_incomplete"
)

audit["release_decision"] = {
    "required_paths_ok": required_ok,
    "required_docs_ok": docs_ok,
    "required_data_records_ok": records_ok,
    "can_continue": required_ok and docs_ok and records_ok,
    "next_step": "production_deployment_provider_readiness",
}

json_path = DATA / "step105_local_production_release_bundle_audit.json"
md_path = DOCS / "STEP_105_LOCAL_PRODUCTION_RELEASE_BUNDLE_AUDIT.md"

json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

def table_rows(mapping):
    return "\n".join(
        f"| `{key}` | {'OK' if value else 'MISSING'} |"
        for key, value in mapping.items()
    )

md = f"""# Step 105 — Local Production Release Bundle Audit

Generated: {now}

## Status

**Release bundle status:** `{audit["release_bundle_status"]}`

## Required Paths

| Path | Status |
|---|---|
{table_rows(audit["required_paths"])}

## Optional Paths

| Path | Status |
|---|---|
{table_rows(audit["optional_paths"])}

## Required Release Docs

| File | Status |
|---|---|
{table_rows(audit["required_docs"])}

## Required Data Records

| File | Status |
|---|---|
{table_rows(audit["required_data_records"])}

## Release Decision

- Required paths OK: `{required_ok}`
- Required docs OK: `{docs_ok}`
- Required data records OK: `{records_ok}`
- Can continue: `{required_ok and docs_ok and records_ok}`

## Next Step

Production deployment provider readiness.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_105_LOCAL_PRODUCTION_RELEASE_BUNDLE_AUDIT_COMPLETE")
print("json_path", json_path)
print("md_path", md_path)
print("release_bundle_status", audit["release_bundle_status"])
print("required_paths_ok", required_ok)
print("required_docs_ok", docs_ok)
print("required_data_records_ok", records_ok)
print("can_continue", required_ok and docs_ok and records_ok)
print("STEP_105_OK")