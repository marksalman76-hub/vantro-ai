from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "production_env_checklist.json"

ENV = {
    "backend_required_before_launch": [
        "ADMIN_PLATFORM_TOKEN",
        "DATABASE_URL",
        "REDIS_URL",
        "QUEUE_BACKEND",
        "OPENAI_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "BREVO_API_KEY",
        "OWNER_APPROVAL_REQUIRED",
        "LIVE_EXTERNAL_CALLS_ENABLED",
        "RATE_SHAPING_ENABLED",
        "RATE_SHAPING_MODE"
    ],
    "worker_required_before_launch": [
        "REDIS_URL",
        "QUEUE_BACKEND",
        "WORKER_LIVE_EXECUTION_ENABLED",
        "LIVE_EXTERNAL_CALLS_ENABLED",
        "OWNER_APPROVAL_REQUIRED",
        "WORKER_HEARTBEAT_SECONDS",
        "OPENAI_API_KEY"
    ],
    "frontend_required_before_launch": [
        "NEXT_PUBLIC_API_BASE_URL",
        "NEXT_PUBLIC_APP_BASE_URL"
    ],
    "optional_integrations_later": [
        "SHOPIFY_CLIENT_ID",
        "SHOPIFY_CLIENT_SECRET",
        "GOHIGHLEVEL_API_KEY",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "META_APP_ID",
        "META_APP_SECRET"
    ],
    "must_stay_disabled_until_owner_approval": {
        "LIVE_EXTERNAL_CALLS_ENABLED": "false",
        "WORKER_LIVE_EXECUTION_ENABLED": "false"
    }
}

OUT.write_text(json.dumps(ENV, indent=2), encoding="utf-8")

print("PRODUCTION_ENV_CHECKLIST_CREATED")
print(json.dumps(ENV, indent=2))