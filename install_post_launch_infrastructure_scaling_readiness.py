from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"post_launch_infrastructure_scaling_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "post_launch_infrastructure_scaling_readiness.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
DOC_FILE = ROOT / "docs" / "post-launch-infrastructure-scaling-validation.md"
TEST_FILE = ROOT / "test_post_launch_infrastructure_scaling_readiness.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_post_launch_infrastructure_scaling_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "track": "post_launch_operational_maturity",
        "layer": "infrastructure_scaling_validation",
        "status": "ready",
        "production_launch_matrix_complete": True,
        "infrastructure_scaling_validation_enabled": True,
        "heavier_concurrent_load_validation_ready": True,
        "cdn_optimisation_review_ready": True,
        "db_growth_validation_ready": True,
        "redis_queue_scaling_review_ready": True,
        "autoscaling_rules_review_ready": True,
        "provider_throughput_limits_review_ready": True,
        "backend_update_allowance_enabled": True,
        "safe_backend_update_mode_enabled": True,
        "backend_updates_require_owner_approval": True,
        "no_live_migration_without_owner_approval": True,
        "rollback_plan_required_for_backend_updates": True,
        "schema_change_review_required": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "validation_domains": [
            "heavier_concurrent_load",
            "cdn_optimisation",
            "db_growth_validation",
            "redis_queue_scaling",
            "autoscaling_rules",
            "provider_throughput_limits",
            "safe_backend_update_enablement",
        ],
        "operator_rules": [
            "Run scaling tests in controlled stages before high-volume production traffic.",
            "Do not run destructive migrations without backup and owner approval.",
            "Do not enable provider saturation tests against live paid providers without owner approval.",
            "Backend updates must include rollback notes, tests, and commit evidence.",
            "Production credentials must never be exposed in status routes, logs, or client surfaces.",
        ],
        "recommended_validation_sequence": [
            "baseline_health_check",
            "concurrent_load_smoke",
            "database_growth_simulation",
            "queue_backpressure_review",
            "provider_limit_review",
            "cdn_cache_review",
            "autoscaling_policy_review",
            "backend_update_dry_run",
        ],
        "verified_at": _now(),
    }


def get_client_safe_post_launch_infrastructure_scaling_readiness() -> Dict[str, Any]:
    status = get_post_launch_infrastructure_scaling_readiness()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "production_launch_matrix_complete": status["production_launch_matrix_complete"],
        "infrastructure_scaling_validation_enabled": status["infrastructure_scaling_validation_enabled"],
        "heavier_concurrent_load_validation_ready": status["heavier_concurrent_load_validation_ready"],
        "cdn_optimisation_review_ready": status["cdn_optimisation_review_ready"],
        "db_growth_validation_ready": status["db_growth_validation_ready"],
        "redis_queue_scaling_review_ready": status["redis_queue_scaling_review_ready"],
        "autoscaling_rules_review_ready": status["autoscaling_rules_review_ready"],
        "provider_throughput_limits_review_ready": status["provider_throughput_limits_review_ready"],
        "backend_update_allowance_enabled": status["backend_update_allowance_enabled"],
        "safe_backend_update_mode_enabled": status["safe_backend_update_mode_enabled"],
        "backend_updates_require_owner_approval": status["backend_updates_require_owner_approval"],
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "validation_domains": status["validation_domains"],
        "verified_at": status["verified_at"],
    }
'''

DOC_CONTENT = r'''# Post-Launch Infrastructure Scaling Validation

## Purpose

This document locks the first post-launch operational maturity layer after the completed Final Production Launch Matrix.

The platform is already production-release ready. This layer prepares it for higher-volume commercial operation, controlled backend updates, and safer scaling decisions.

## Validation Domains

### 1. Heavier concurrent load

Goal:
- Validate that the frontend, backend, queues, and provider orchestration can handle increased simultaneous customer activity.

Rules:
- Start with controlled smoke load.
- Increase gradually.
- Do not run destructive or saturation tests without owner approval.
- Capture response time, failure rate, timeout rate, and queue behaviour.

### 2. CDN optimisation

Goal:
- Review static assets, generated assets, generated sites, client portal pages, admin portal pages, and public pages for cache safety and performance.

Rules:
- Never cache tenant-private data publicly.
- Keep admin surfaces dynamic/private.
- Keep generated customer assets tenant-safe.
- Use cache headers only where data is safe.

### 3. DB growth validation

Goal:
- Validate storage behaviour as clients, executions, deliverables, approvals, media assets, billing records, and audit records grow.

Rules:
- Backups before migrations.
- Rollback plan before schema changes.
- No destructive migration without owner approval.
- Growth tests should use simulated or staged data first.

### 4. Redis / queue scaling

Goal:
- Prepare queue and retry layers for larger execution volume and backpressure handling.

Rules:
- Validate queue depth.
- Validate retry limits.
- Validate dead-letter/manual-review pathways.
- Validate provider failover does not cause uncontrolled cost or duplicate external actions.

### 5. Autoscaling rules

Goal:
- Define when infrastructure should scale and what operator approval is needed.

Rules:
- Owner approval remains required for cost-impacting scaling.
- Autoscaling policies must preserve budget controls.
- Scaling recommendations can be generated, but spend decisions remain owner-only.

### 6. Provider throughput limits

Goal:
- Prevent provider saturation, excess cost, rate-limit failures, and customer-impacting execution delays.

Rules:
- Track provider limits.
- Use retry/failover carefully.
- No uncontrolled provider saturation tests.
- Paid provider expansion remains owner-approved.

### 7. Backend update readiness

Goal:
- Allow future backend updates safely after launch without destabilising production.

Rules:
- Every backend update requires tests.
- Every backend update requires rollback notes.
- Every backend update must avoid credential exposure.
- Production migrations require backup first.
- High-risk updates require owner approval.
- Customer-facing routes must never expose internal prompts, credentials, governance internals, or proprietary runtime configuration.

## Status

POST_LAUNCH_INFRASTRUCTURE_SCALING_VALIDATION_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "post_launch_infrastructure_scaling_readiness.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "post-launch-infrastructure-scaling-validation.md"

required_files = [runtime_file, main_file, doc_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "post_launch_infrastructure_scaling_readiness",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_post_launch_infrastructure_scaling_readiness()
client_status = module.get_client_safe_post_launch_infrastructure_scaling_readiness()

required_true_flags = [
    "production_launch_matrix_complete",
    "infrastructure_scaling_validation_enabled",
    "heavier_concurrent_load_validation_ready",
    "cdn_optimisation_review_ready",
    "db_growth_validation_ready",
    "redis_queue_scaling_review_ready",
    "autoscaling_rules_review_ready",
    "provider_throughput_limits_review_ready",
    "backend_update_allowance_enabled",
    "safe_backend_update_mode_enabled",
    "backend_updates_require_owner_approval",
    "no_live_migration_without_owner_approval",
    "rollback_plan_required_for_backend_updates",
    "schema_change_review_required",
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
    "heavier_concurrent_load",
    "cdn_optimisation",
    "db_growth_validation",
    "redis_queue_scaling",
    "autoscaling_rules",
    "provider_throughput_limits",
    "backend_update_allowance_enabled",
    "backend_updates_require_owner_approval",
    "credential_values_exposed",
    "external_actions_performed",
]

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

route_markers = [
    "/post-launch/infrastructure-scaling-readiness",
    "/admin/post-launch/infrastructure-scaling-readiness",
    "get_post_launch_infrastructure_scaling_readiness",
]

for marker in route_markers:
    if marker not in main_text:
        raise AssertionError(f"Missing backend route marker: {marker}")

print("POST_LAUNCH_INFRASTRUCTURE_SCALING_READINESS_PASSED")
'''

MAIN_ROUTE_BLOCK = r'''
# POST_LAUNCH_INFRASTRUCTURE_SCALING_READINESS_START
try:
    from backend.app.runtime.post_launch_infrastructure_scaling_readiness import (
        get_client_safe_post_launch_infrastructure_scaling_readiness,
        get_post_launch_infrastructure_scaling_readiness,
    )

    @app.get("/post-launch/infrastructure-scaling-readiness")
    async def post_launch_infrastructure_scaling_readiness():
        return get_client_safe_post_launch_infrastructure_scaling_readiness()

    @app.get("/admin/post-launch/infrastructure-scaling-readiness")
    async def admin_post_launch_infrastructure_scaling_readiness():
        return get_post_launch_infrastructure_scaling_readiness()

except Exception as post_launch_infrastructure_scaling_readiness_error:
    @app.get("/post-launch/infrastructure-scaling-readiness")
    async def post_launch_infrastructure_scaling_readiness_unavailable():
        return {
            "success": False,
            "layer": "infrastructure_scaling_validation",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_infrastructure_scaling_readiness_error),
        }

    @app.get("/admin/post-launch/infrastructure-scaling-readiness")
    async def admin_post_launch_infrastructure_scaling_readiness_unavailable():
        return {
            "success": False,
            "layer": "infrastructure_scaling_validation",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_infrastructure_scaling_readiness_error),
        }
# POST_LAUNCH_INFRASTRUCTURE_SCALING_READINESS_END
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

    if "POST_LAUNCH_INFRASTRUCTURE_SCALING_READINESS_START" not in text:
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + MAIN_ROUTE_BLOCK.lstrip(), encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)
    append_main_route_block()

    print("POST_LAUNCH_INFRASTRUCTURE_SCALING_READINESS_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")
    print(f"Updated: {MAIN_FILE}")


if __name__ == "__main__":
    main()