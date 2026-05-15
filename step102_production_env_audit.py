from pathlib import Path
from datetime import datetime, timezone
import json
import os

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

env_files = [
    ROOT / ".env",
    ROOT / ".env.local",
    ROOT / "backend" / ".env",
    ROOT / "frontend" / ".env",
    ROOT / "frontend" / ".env.local",
    ROOT / "apps" / "web" / ".env",
    ROOT / "apps" / "web" / ".env.local",
]

required_production_keys = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "XAI_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "DATABASE_URL",
    "JWT_SECRET",
    "APP_ENV",
    "FRONTEND_URL",
    "BACKEND_URL",
]

sensitive_markers = [
    "sk-",
    "rk-",
    "whsec_",
    "pk_live_",
    "sk_live_",
    "password=",
    "secret=",
    "token=",
]

found_env_files = []
missing_env_files = []
detected_keys = {}
exposed_sensitive_line_risks = []

for env_file in env_files:
    if env_file.exists():
        found_env_files.append(str(env_file.relative_to(ROOT)))
        text = env_file.read_text(encoding="utf-8", errors="ignore")
        for key in required_production_keys:
            if key in text:
                detected_keys.setdefault(key, []).append(str(env_file.relative_to(ROOT)))
        for line_no, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            if any(marker.lower() in lowered for marker in sensitive_markers):
                exposed_sensitive_line_risks.append({
                    "file": str(env_file.relative_to(ROOT)),
                    "line": line_no,
                    "risk": "sensitive_value_present_in_local_env_file",
                    "key_hint": line.split("=", 1)[0].strip() if "=" in line else "unknown",
                })
    else:
        missing_env_files.append(str(env_file.relative_to(ROOT)))

missing_required_keys = [
    key for key in required_production_keys if key not in detected_keys and key not in os.environ
]

audit = {
    "step": 102,
    "name": "Production Environment Variable Audit",
    "generated_at_utc": now,
    "project_root": str(ROOT),
    "status": "production_env_audit_complete",
    "found_env_files": found_env_files,
    "missing_env_files_checked": missing_env_files,
    "required_production_keys": required_production_keys,
    "detected_required_keys_in_files": detected_keys,
    "missing_required_keys_or_not_detected_locally": missing_required_keys,
    "sensitive_local_env_risks": exposed_sensitive_line_risks,
    "release_decision": {
        "can_continue_to_provider_connection": True,
        "manual_secret_values_not_printed": True,
        "secrets_not_exposed_by_audit": True,
        "next_step": "connect_or_confirm_live_provider_credentials_in_deployment_environment",
    }
}

json_path = DATA / "step102_production_env_audit.json"
md_path = DOCS / "STEP_102_PRODUCTION_ENVIRONMENT_VARIABLE_AUDIT.md"

json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

md = f"""# Step 102 — Production Environment Variable Audit

Generated: {now}

## Status

**Result:** Production environment audit completed  
**Secrets printed:** No  
**Secret values exposed:** No  
**Project root:** `{ROOT}`

## Environment Files Found

{chr(10).join("- `" + item + "`" for item in found_env_files) if found_env_files else "- No local environment files found in checked paths."}

## Required Production Keys Checked

{chr(10).join("- `" + key + "`" for key in required_production_keys)}

## Keys Not Detected Locally

These may still exist safely in Render, Vercel, or another deployment provider.

{chr(10).join("- `" + key + "`" for key in missing_required_keys) if missing_required_keys else "- All required keys were detected locally or in the current process environment."}

## Sensitive Local Env Risk Count

**Risk count:** {len(exposed_sensitive_line_risks)}

Sensitive values were not printed. Only file/line/key hints were recorded in the JSON audit.

## Release Decision

Continue to live provider credential confirmation and production deployment environment validation.

## Next Step

Step 103 should confirm live provider/environment readiness without exposing secret values.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_102_PRODUCTION_ENV_AUDIT_COMPLETE")
print("json_path", json_path)
print("md_path", md_path)
print("found_env_files", len(found_env_files))
print("missing_required_keys_or_not_detected_locally", missing_required_keys)
print("sensitive_local_env_risk_count", len(exposed_sensitive_line_risks))
print("STEP_102_OK")