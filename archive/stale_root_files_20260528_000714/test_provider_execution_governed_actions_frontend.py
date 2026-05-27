from pathlib import Path

ROOT = Path.cwd()

provider = (ROOT / "frontend/src/app/admin/provider-execution/page.tsx").read_text(encoding="utf-8")
routes = {
    "retry": ROOT / "frontend/src/app/api/admin-provider-execution/retry/route.ts",
    "requeue": ROOT / "frontend/src/app/api/admin-provider-execution/requeue/route.ts",
    "cancel": ROOT / "frontend/src/app/api/admin-provider-execution/cancel/route.ts",
}

for name, path in routes.items():
    assert path.exists(), f"Missing frontend action proxy route: {path}"
    text = path.read_text(encoding="utf-8")
    assert f"/provider-execution-admin-visibility/actions/{name}" in text
    assert "ADMIN_PLATFORM_TOKEN" in text
    assert "credential_values_exposed: false" in text

checks = {
    "run_governed_action": "runGovernedAction" in provider,
    "retry_button_enabled": 'runGovernedAction("retry")' in provider,
    "requeue_button_enabled": 'runGovernedAction("requeue")' in provider,
    "cancel_button_enabled": 'runGovernedAction("cancel")' in provider,
    "governance_wording": "protected backend governance routes" in provider,
    "credential_safe_wording": "do not expose internal credentials" in provider,
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Frontend governed action checks failed: {failed}"

for name, content in {"provider": provider, **{k: v.read_text(encoding='utf-8') for k, v in routes.items()}}.items():
    forbidden = ["sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"]
    exposed = [item for item in forbidden if item in content]
    assert not exposed, f"Forbidden secret marker found in {name}: {exposed}"

print("PROVIDER_EXECUTION_GOVERNED_ACTIONS_FRONTEND_TESTS_PASSED")
print("frontend_action_proxy_ready", True)
print("dashboard_buttons_wired", True)
print("credential_values_exposed", False)
