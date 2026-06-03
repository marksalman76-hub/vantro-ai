from pathlib import Path
import re

ROOT = Path.cwd()

required_files = [
    ROOT / "frontend" / "src" / "lib" / "securityGovernanceClosure.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "security-governance-closure-status" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "admin-security-governance-closure-status" / "route.ts",
]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

lib_text = required_files[0].read_text(encoding="utf-8")

required_markers = [
    "owner_approval_required_for_spend",
    "autonomous_spend_blocked",
    "autonomous_scaling_blocked",
    "autonomous_strategy_changes_blocked",
    "autonomous_retraining_blocked",
    "client_prompt_visibility_blocked",
    "proprietary_logic_visibility_blocked",
    "tenant_isolation_enforced",
    "audit_logging_active",
    "credential_values_exposed: false",
]

for marker in required_markers:
    if marker not in lib_text:
        raise AssertionError(f"Missing security/governance marker: {marker}")

if re.search(r"credential_values_exposed:\s*true", lib_text):
    raise AssertionError("Credential exposure violation found")

print("ROW17_SECURITY_GOVERNANCE_CLOSURE_PASSED")
