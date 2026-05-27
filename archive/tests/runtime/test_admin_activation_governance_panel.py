from pathlib import Path

text = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

assert "Activation Governance" in text
assert "/api/admin-activation-governance/summary" in text
assert "loadActivationGovernance" in text
assert "activation_ledger_event_count" in text
assert "blocked_execution_decision_count" in text
assert "owner_admin_review_required_count" in text
assert "credential_values_exposed" in text

print("ADMIN_ACTIVATION_GOVERNANCE_PANEL_TESTS_PASSED")
print("panel_present", "Activation Governance" in text)
print("summary_api_wired", "/api/admin-activation-governance/summary" in text)
print("credential_marker", "credential_values_exposed" in text)
