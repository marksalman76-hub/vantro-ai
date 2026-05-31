from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

CHECKS = {
    "redis_adapter_exists": "backend/app/runtime/queue_adapter.py",
    "worker_orchestration_exists": "backend/app/runtime/worker_orchestration_runtime.py",
    "rate_policy_exists": "backend/app/core/rate_shaping_policy.py",
    "render_manifest_exists": "render.yaml",
    "stripe_payment_script_exists": "scripts/stripe/live-payment-test.js",
    "subscription_flow_script_exists": "scripts/stripe/subscription-flows.js",
    "support_workflow_script_exists": "scripts/support/setup-workflows.js",
    "gdpr_tooling_exists": "scripts/tenants/gdpr-tooling.js",
    "dashboard_deploy_script_exists": "scripts/dashboards/deploy.js",
    "qa_automation_exists": "scripts/qa/automate.js",
    "enterprise_onboarding_exists": "scripts/onboarding/enterprise.js",
}

def exists(path):
    return (ROOT / path).exists()

def main():
    checks = {name: exists(path) for name, path in CHECKS.items()}
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)

    report = {
        "audit": "deferred_activation_items",
        "score": f"{passed}/{total}",
        "checks": checks,
        "activation_order": [
            "Final Render smoke verification",
            "Rate-shaping middleware wiring",
            "Managed Redis activation",
            "Live worker process activation",
            "Live dashboard deployment",
            "External helpdesk integration",
            "Live QA blocking enforcement",
            "Owner-approved Stripe live transaction",
            "Webhook/invoice confirmation",
            "Real tenant export/delete workflow"
        ],
        "status": "DEFERRED_ACTIVATION_READY_FOR_CONTROLLED_SEQUENCE" if passed == total else "DEFERRED_ACTIVATION_INCOMPLETE",
        "safety": {
            "do_not_run_real_charges_without_owner_confirmation": True,
            "do_not_delete_real_tenants_without explicit owner approval": True,
            "do_not_enable live external execution automatically": True
        }
    }

    Path("deferred_activation_items_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("DEFERRED_ACTIVATION_ITEMS_AUDIT_COMPLETE")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()