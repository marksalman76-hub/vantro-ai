from pathlib import Path

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend/src/app/admin/provider-execution/page.tsx",
    ROOT / "frontend/src/app/api/admin-provider-execution/status/route.ts",
    ROOT / "frontend/src/app/api/admin-provider-execution/summary/route.ts",
]

for path in required_files:
    assert path.exists(), f"Missing required file: {path}"

page = required_files[0].read_text(encoding="utf-8")
status_route = required_files[1].read_text(encoding="utf-8")
summary_route = required_files[2].read_text(encoding="utf-8")

checks = {
    "dashboard_title": "Provider Execution Dashboard" in page,
    "job_table": "Live Provider Jobs" in page,
    "retry_timeout_visibility": "Retry / Timeout Visibility" in page,
    "delivery_packet_visibility": "Delivery Packet Visibility" in page,
    "runtime_polling": "setInterval(loadProviderExecution, 15000)" in page,
    "customer_safe_wording": "Customer-safe" in page,
    "status_proxy_route": "/provider-execution-admin-visibility/status" in status_route,
    "summary_proxy_route": "/provider-execution-admin-visibility/summary" in summary_route,
    "server_side_admin_token_status": "ADMIN_PLATFORM_TOKEN" in status_route,
    "server_side_admin_token_summary": "ADMIN_PLATFORM_TOKEN" in summary_route,
    "credential_exposure_false_status": "credential_values_exposed: false" in status_route,
    "credential_exposure_false_summary": "credential_values_exposed: false" in summary_route,
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Checks failed: {failed}"

for content_name, content in [
    ("page", page),
    ("status_route", status_route),
    ("summary_route", summary_route),
]:
    forbidden = [
        "sk-",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
    ]
    exposed = [item for item in forbidden if item in content]
    assert not exposed, f"Forbidden secret marker found in {content_name}: {exposed}"

print("FRONTEND_PROVIDER_EXECUTION_ADMIN_DASHBOARD_TESTS_PASSED")
print("dashboard_page_ready", True)
print("api_proxy_ready", True)
print("credential_values_exposed", False)
