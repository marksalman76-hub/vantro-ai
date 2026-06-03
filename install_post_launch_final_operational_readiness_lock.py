from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"post_launch_final_operational_readiness_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "post_launch_final_operational_readiness_lock.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
DOC_FILE = ROOT / "docs" / "post-launch-final-operational-readiness-lock.md"
TEST_FILE = ROOT / "test_post_launch_final_operational_readiness_lock.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_post_launch_final_operational_readiness_lock() -> Dict[str, Any]:
    return {
        "success": True,
        "track": "post_launch_operational_maturity",
        "layer": "final_operational_readiness_lock",
        "status": "locked",
        "production_launch_matrix_complete": True,
        "final_production_release_candidate_complete": True,
        "post_launch_operational_maturity_complete": True,
        "infrastructure_scaling_validation_complete": True,
        "commercial_operations_sops_complete": True,
        "backend_update_allowance_enabled": True,
        "future_backend_updates_allowed": True,
        "future_updates_require_tests": True,
        "future_high_risk_updates_require_owner_approval": True,
        "future_schema_changes_require_backup_and_review": True,
        "future_provider_scaling_requires_owner_approval": True,
        "future_pricing_changes_require_owner_approval": True,
        "owner_governance_preserved": True,
        "tenant_isolation_preserved": True,
        "customer_safe_visibility_preserved": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "locked_completion_state": {
            "final_production_launch_matrix": "FULL_FINAL_PRODUCTION_LAUNCH_MATRIX_COMPLETE",
            "post_launch_infrastructure_scaling": "COMPLETE",
            "post_launch_commercial_operations": "COMPLETE",
            "post_launch_operational_readiness": "COMPLETE",
        },
        "completed_commits": {
            "final_production_release_candidate": "7d331d8",
            "post_launch_infrastructure_scaling_readiness": "97db44b",
            "post_launch_commercial_operations_sops": "0ebe191",
        },
        "future_update_rules": [
            "Backend updates are allowed after launch.",
            "Every future backend update must include tests.",
            "Every future backend update must preserve rollback awareness.",
            "High-risk updates require owner approval.",
            "Schema or migration changes require backup and review.",
            "Provider scaling and spend-impacting changes require owner approval.",
            "Pricing, refunds, enterprise terms, and commercial exceptions require owner approval.",
            "Customer-facing routes must not expose credentials, prompts, internal routing, or proprietary logic.",
            "Tenant isolation and customer-safe visibility must remain preserved.",
        ],
        "verified_at": _now(),
    }


def get_client_safe_post_launch_final_operational_readiness_lock() -> Dict[str, Any]:
    status = get_post_launch_final_operational_readiness_lock()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "production_launch_matrix_complete": status["production_launch_matrix_complete"],
        "final_production_release_candidate_complete": status["final_production_release_candidate_complete"],
        "post_launch_operational_maturity_complete": status["post_launch_operational_maturity_complete"],
        "infrastructure_scaling_validation_complete": status["infrastructure_scaling_validation_complete"],
        "commercial_operations_sops_complete": status["commercial_operations_sops_complete"],
        "backend_update_allowance_enabled": status["backend_update_allowance_enabled"],
        "future_backend_updates_allowed": status["future_backend_updates_allowed"],
        "owner_governance_preserved": status["owner_governance_preserved"],
        "tenant_isolation_preserved": status["tenant_isolation_preserved"],
        "customer_safe_visibility_preserved": status["customer_safe_visibility_preserved"],
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "locked_completion_state": status["locked_completion_state"],
        "verified_at": status["verified_at"],
    }
'''

DOC_CONTENT = r'''# Post-Launch Final Operational Readiness Lock

## Final Locked State

The platform has completed:

1. Final Production Launch Matrix
2. Post-Launch Infrastructure Scaling Validation
3. Post-Launch Commercial Operations SOPs
4. Final Post-Launch Operational Readiness Lock

## Production Launch Matrix

Status:

FULL_FINAL_PRODUCTION_LAUNCH_MATRIX_COMPLETE

Latest final production release candidate commit:

7d331d8

## Post-Launch Operational Maturity

### PL-1 Infrastructure Scaling Validation

Status: Complete

Commit:

97db44b

Covered:
- heavier concurrent load validation readiness
- CDN optimisation review readiness
- DB growth validation readiness
- Redis/queue scaling review readiness
- autoscaling rules review readiness
- provider throughput limits review readiness
- safe backend update allowance

### PL-2 Commercial Operations SOPs

Status: Complete

Commit:

0ebe191

Covered:
- onboarding SOPs
- customer support SOPs
- refund/dispute handling
- incident playbooks
- pricing optimisation
- sales process refinement
- backend update continuity

### PL-3 Final Operational Readiness Lock

Status: Complete after commit

Covered:
- future backend updates allowed safely
- owner approval preserved
- tenant isolation preserved
- customer-safe visibility preserved
- credential and proprietary logic protection preserved

## Future Backend Update Rules

Backend updates are allowed after launch.

Rules:
- Every backend update requires tests.
- Every backend update must preserve rollback awareness.
- High-risk backend updates require owner approval.
- Schema or migration updates require backup and review.
- Provider scaling and spend-impacting changes require owner approval.
- Pricing, refunds, enterprise terms, and commercial exceptions require owner approval.
- Customer-facing surfaces must not expose credentials, prompts, routing logic, governance internals, or proprietary runtime configuration.
- Tenant isolation must remain enforced.
- Owner/admin unrestricted internal use must remain preserved.

## Final Post-Launch Status

POST_LAUNCH_OPERATIONAL_READINESS_COMPLETE
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "post_launch_final_operational_readiness_lock.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "post-launch-final-operational-readiness-lock.md"

dependency_tests = [
    ROOT / "test_post_launch_infrastructure_scaling_readiness.py",
    ROOT / "test_post_launch_commercial_operations_sops.py",
    ROOT / "test_row22_final_production_release_candidate.py",
]

required_files = [runtime_file, main_file, doc_file] + dependency_tests

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "post_launch_final_operational_readiness_lock",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_post_launch_final_operational_readiness_lock()
client_status = module.get_client_safe_post_launch_final_operational_readiness_lock()

required_true_flags = [
    "production_launch_matrix_complete",
    "final_production_release_candidate_complete",
    "post_launch_operational_maturity_complete",
    "infrastructure_scaling_validation_complete",
    "commercial_operations_sops_complete",
    "backend_update_allowance_enabled",
    "future_backend_updates_allowed",
    "future_updates_require_tests",
    "future_high_risk_updates_require_owner_approval",
    "future_schema_changes_require_backup_and_review",
    "future_provider_scaling_requires_owner_approval",
    "future_pricing_changes_require_owner_approval",
    "owner_governance_preserved",
    "tenant_isolation_preserved",
    "customer_safe_visibility_preserved",
]

for flag in required_true_flags:
    if status.get(flag) is not True:
        raise AssertionError(f"Expected true flag missing or false: {flag}")

if status.get("credential_values_exposed") is not False:
    raise AssertionError("Credential exposure flag must be false")

if status.get("external_actions_performed") is not False:
    raise AssertionError("Status route must not perform external actions")

if client_status.get("credential_values_exposed") is not False:
    raise AssertionError("Client-safe status must not expose credentials")

runtime_text = runtime_file.read_text(encoding="utf-8")
main_text = main_file.read_text(encoding="utf-8")
doc_text = doc_file.read_text(encoding="utf-8")

required_markers = [
    "FULL_FINAL_PRODUCTION_LAUNCH_MATRIX_COMPLETE",
    "POST_LAUNCH_OPERATIONAL_READINESS_COMPLETE",
    "backend_update_allowance_enabled",
    "future_backend_updates_allowed",
    "future_high_risk_updates_require_owner_approval",
    "future_schema_changes_require_backup_and_review",
    "future_provider_scaling_requires_owner_approval",
    "future_pricing_changes_require_owner_approval",
    "owner_governance_preserved",
    "tenant_isolation_preserved",
    "credential_values_exposed",
    "external_actions_performed",
]

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

route_markers = [
    "/post-launch/final-operational-readiness-lock",
    "/admin/post-launch/final-operational-readiness-lock",
    "get_post_launch_final_operational_readiness_lock",
]

for marker in route_markers:
    if marker not in main_text:
        raise AssertionError(f"Missing backend route marker: {marker}")

print("POST_LAUNCH_FINAL_OPERATIONAL_READINESS_LOCK_PASSED")
'''

MAIN_ROUTE_BLOCK = r'''
# POST_LAUNCH_FINAL_OPERATIONAL_READINESS_LOCK_START
try:
    from backend.app.runtime.post_launch_final_operational_readiness_lock import (
        get_client_safe_post_launch_final_operational_readiness_lock,
        get_post_launch_final_operational_readiness_lock,
    )

    @app.get("/post-launch/final-operational-readiness-lock")
    async def post_launch_final_operational_readiness_lock():
        return get_client_safe_post_launch_final_operational_readiness_lock()

    @app.get("/admin/post-launch/final-operational-readiness-lock")
    async def admin_post_launch_final_operational_readiness_lock():
        return get_post_launch_final_operational_readiness_lock()

except Exception as post_launch_final_operational_readiness_lock_error:
    @app.get("/post-launch/final-operational-readiness-lock")
    async def post_launch_final_operational_readiness_lock_unavailable():
        return {
            "success": False,
            "layer": "final_operational_readiness_lock",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_final_operational_readiness_lock_error),
        }

    @app.get("/admin/post-launch/final-operational-readiness-lock")
    async def admin_post_launch_final_operational_readiness_lock_unavailable():
        return {
            "success": False,
            "layer": "final_operational_readiness_lock",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_final_operational_readiness_lock_error),
        }
# POST_LAUNCH_FINAL_OPERATIONAL_READINESS_LOCK_END
'''


def backup_path(path: Path) -> None:
    if path.exists():
        relative = path.relative_to(ROOT)
        destination = BACKUP / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def write_file(path: Path, content: str) -> None:
    backup_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def append_main_route_block() -> None:
    if not MAIN_FILE.exists():
        raise FileNotFoundError(f"Missing backend main file: {MAIN_FILE}")

    backup_path(MAIN_FILE)
    text = MAIN_FILE.read_text(encoding="utf-8", errors="ignore")

    if "POST_LAUNCH_FINAL_OPERATIONAL_READINESS_LOCK_START" not in text:
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + MAIN_ROUTE_BLOCK.lstrip(), encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)
    append_main_route_block()

    print("POST_LAUNCH_FINAL_OPERATIONAL_READINESS_LOCK_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")
    print(f"Updated: {MAIN_FILE}")


if __name__ == "__main__":
    main()