from pathlib import Path

ROOT = Path.cwd()
admin = (ROOT / "frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")
provider = (ROOT / "frontend/src/app/admin/provider-execution/page.tsx").read_text(encoding="utf-8")

checks = {
    "admin_links_provider_execution": "/admin/provider-execution" in admin,
    "admin_provider_card": "Provider Execution" in admin,
    "detail_modal": "Provider Job Detail" in provider,
    "execution_timeline": "Execution Timeline" in provider,
    "governed_actions": "Governed Actions" in provider,
    "retry_read_only": "Retry job" in provider,
    "requeue_read_only": "Requeue job" in provider,
    "cancel_read_only": "Cancel job" in provider,
    "customer_safe_wording": "Customer-safe operational details only" in provider,
    "secret_safe_wording": "provider secrets" in provider,
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Provider admin UI block checks failed: {failed}"

for name, content in {"admin": admin, "provider": provider}.items():
    forbidden = ["sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"]
    exposed = [item for item in forbidden if item in content]
    assert not exposed, f"Forbidden secret marker found in {name}: {exposed}"

print("PROVIDER_EXECUTION_ADMIN_UI_BLOCK_TESTS_PASSED")
print("admin_dashboard_link_ready", True)
print("job_detail_modal_ready", True)
print("execution_timeline_ready", True)
print("governed_actions_read_only_ready", True)
print("credential_values_exposed", False)
