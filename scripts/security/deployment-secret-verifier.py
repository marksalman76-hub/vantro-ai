from pathlib import Path
import json

ROOT = Path.cwd()
manifest = json.loads((ROOT / "config" / "security" / "production-secret-manifest.json").read_text(encoding="utf-8"))

targets = []
for secret in manifest["required_secrets"]:
    targets.append({
        "secret": secret,
        "render_required": secret in [
            "ADMIN_PLATFORM_TOKEN",
            "JWT_SECRET",
            "SESSION_SECRET",
            "DATABASE_URL",
            "OPENAI_API_KEY",
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET",
            "SMTP_PASSWORD",
            "BREVO_API_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ],
        "vercel_required": secret in [
            "ADMIN_PLATFORM_TOKEN",
            "SESSION_SECRET",
        ],
        "supabase_required": secret in [
            "DATABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
        ],
        "manual_owner_verification_required": True,
    })

report = {
    "success": True,
    "mode": "deployment_secret_verification_checklist",
    "production_rotation_executed": False,
    "owner_approval_required": True,
    "targets": targets,
}

out = ROOT / "telemetry" / "security" / "deployment-secret-verifier.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("DEPLOYMENT_SECRET_VERIFIER_CREATED")
print("TARGETS:", len(targets))
print("OWNER_APPROVAL_REQUIRED:true")
