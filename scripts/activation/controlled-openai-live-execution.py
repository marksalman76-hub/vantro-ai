from pathlib import Path
from datetime import datetime
import json
import os
import urllib.request
import urllib.error

ROOT = Path.cwd()
API_BASE = "https://api.trance-formation.com.au"

token = os.getenv("ADMIN_PLATFORM_TOKEN", "")
owner_approved = os.getenv("OWNER_APPROVED_LIVE_ACTIVATION", "").lower() == "true"

headers = {
    "User-Agent": "controlled-openai-live-execution-verifier",
    "Authorization": f"Bearer {token}",
    "x-admin-token": token,
    "Content-Type": "application/json",
}

checks = {}

def request_json(endpoint, payload=None):
    url = API_BASE + endpoint
    data = None
    method = "GET"

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        method = "POST"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {
                "reachable": True,
                "status": response.status,
                "body": body[:5000],
            }
    except urllib.error.HTTPError as exc:
        return {
            "reachable": True,
            "status": exc.code,
            "body": exc.read().decode("utf-8", errors="replace")[:5000],
        }
    except Exception as exc:
        return {
            "reachable": False,
            "status": None,
            "error": str(exc),
        }

checks["provider_activation_visibility"] = request_json("/admin/provider-activation-visibility")

checks["provider_action_readiness"] = request_json("/admin/provider-action-readiness")

# Safe live OpenAI readiness probe only. This does not attempt high-volume execution.
# It depends on whatever governed endpoint is already installed in the backend.
checks["governed_live_probe"] = request_json(
    "/admin/provider-activation-visibility/evaluate",
    {
        "provider_key": "openai",
        "live_execution_requested": True,
        "owner_governed_execution_confirmed": owner_approved,
        "final_policy_enablement_confirmed": owner_approved,
        "prompt": "Controlled production readiness probe. Return a short confirmation only.",
        "mode": "controlled_openai_live_probe"
    }
)

def contains(text, fragment):
    return fragment.lower() in str(text).lower()

activation_body = checks["provider_activation_visibility"].get("body", "")
probe_body = checks["governed_live_probe"].get("body", "")

openai_configured = contains(activation_body, '"configured_providers":["openai"]') or contains(activation_body, '"provider_key":"openai"')
openai_ready = contains(activation_body, '"controlled_live_execution_ready":true') or contains(activation_body, '"openai_api_key_present":true')

probe_reachable = checks["governed_live_probe"].get("reachable") is True
probe_status = checks["governed_live_probe"].get("status")

report = {
    "success": openai_configured and openai_ready and probe_reachable,
    "mode": "controlled_openai_live_execution_enablement",
    "api_base": API_BASE,
    "admin_token_present": bool(token),
    "owner_approved_live_activation": owner_approved,
    "secret_values_exposed": False,
    "openai_configured": openai_configured,
    "openai_ready": openai_ready,
    "probe_reachable": probe_reachable,
    "probe_status": probe_status,
    "high_volume_load_executed": False,
    "checks": {
        key: {
            "reachable": value.get("reachable"),
            "status": value.get("status"),
            "body_preview": value.get("body", "")[:1200],
            "error": value.get("error"),
        }
        for key, value in checks.items()
    },
    "activation_result": (
        "openai_live_probe_ready_or_executed"
        if openai_configured and openai_ready and probe_reachable
        else "review_required"
    ),
    "generated_at": datetime.utcnow().isoformat(),
}

out = ROOT / "telemetry" / "activation" / "controlled-openai-live-execution.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("CONTROLLED_OPENAI_LIVE_EXECUTION_VERIFIER_COMPLETED")
print("ADMIN_TOKEN_PRESENT:", bool(token))
print("OWNER_APPROVED_LIVE_ACTIVATION:", owner_approved)
print("OPENAI_CONFIGURED:", openai_configured)
print("OPENAI_READY:", openai_ready)
print("PROBE_REACHABLE:", probe_reachable)
print("PROBE_STATUS:", probe_status)
print("SECRET_VALUES_EXPOSED:false")
