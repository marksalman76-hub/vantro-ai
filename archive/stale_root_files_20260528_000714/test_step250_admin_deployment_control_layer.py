import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"


def request_json(path, method="GET", payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return exc.code, parsed


tenant_id = "client_step250_manual_deploy"

summary_status, summary = request_json("/admin/deployment-control/summary")

deploy_status, deploy = request_json(
    "/admin/deployment-control/manual-deploy",
    method="POST",
    payload={
        "tenant_id": tenant_id,
        "company_name": "Step 250 Manual Deploy Client",
        "contact_email": "step250-client@example.com",
        "package": "Manual Unlimited",
        "active_agents": [
            "product_copywriting_agent",
            "ugc_creative_agent",
            "analytics_optimisation_agent",
        ],
        "unlimited_credits": True,
    },
)

suspend_status, suspend = request_json(
    "/admin/deployment-control/suspend",
    method="POST",
    payload={
        "tenant_id": tenant_id,
        "reason": "Step 250 suspend smoke test.",
    },
)

reactivate_status, reactivate = request_json(
    "/admin/deployment-control/reactivate",
    method="POST",
    payload={
        "tenant_id": tenant_id,
        "reason": "Step 250 reactivate smoke test.",
    },
)

cancel_status, cancel = request_json(
    "/admin/deployment-control/cancel",
    method="POST",
    payload={
        "tenant_id": tenant_id,
        "reason": "Step 250 cancel smoke test.",
    },
)

list_status, listed = request_json("/admin/deployment-control/list?limit=10")

combined = json.dumps({
    "summary": summary,
    "deploy": deploy,
    "suspend": suspend,
    "reactivate": reactivate,
    "cancel": cancel,
    "listed": listed,
}).lower()

tenant = deploy.get("tenant") or {}

checks = {
    "summary_route_ok": summary_status == 200 and summary.get("success") is True,
    "manual_deploy_ok": deploy_status == 200 and deploy.get("success") is True,
    "tenant_created": tenant.get("tenant_id") == tenant_id,
    "unlimited_credits_enabled": tenant.get("unlimited_credits") is True,
    "activation_link_created": bool(tenant.get("activation_link")),
    "active_agents_assigned": len(tenant.get("active_agents") or []) == 3,
    "suspend_ok": suspend_status == 200 and suspend.get("success") is True,
    "suspend_blocks_execution": suspend.get("execution_blocked") is True,
    "reactivate_ok": reactivate_status == 200 and reactivate.get("success") is True,
    "reactivate_allows_execution": reactivate.get("execution_allowed") is True,
    "cancel_ok": cancel_status == 200 and cancel.get("success") is True,
    "cancel_blocks_execution": cancel.get("execution_blocked") is True,
    "list_route_ok": list_status == 200 and listed.get("success") is True,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_250_ADMIN_DEPLOYMENT_CONTROL_LAYER_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps({
        "summary": summary,
        "deploy": deploy,
        "suspend": suspend,
        "reactivate": reactivate,
        "cancel": cancel,
        "listed": listed,
    }, indent=2))
    raise SystemExit(1)

print("STEP_250_ADMIN_DEPLOYMENT_CONTROL_LAYER_OK")
