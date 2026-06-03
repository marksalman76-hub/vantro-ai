from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"post_launch_commercial_operations_before_{STAMP}"

RUNTIME_FILE = ROOT / "backend" / "app" / "runtime" / "post_launch_commercial_operations_sops.py"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
DOC_FILE = ROOT / "docs" / "post-launch-commercial-operations-sops.md"
TEST_FILE = ROOT / "test_post_launch_commercial_operations_sops.py"

RUNTIME_CONTENT = r'''from datetime import datetime, timezone
from typing import Any, Dict


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_post_launch_commercial_operations_sops() -> Dict[str, Any]:
    return {
        "success": True,
        "track": "post_launch_operational_maturity",
        "layer": "commercial_operations_sops",
        "status": "ready",
        "production_launch_matrix_complete": True,
        "commercial_operations_sops_enabled": True,
        "onboarding_sop_ready": True,
        "customer_support_sop_ready": True,
        "refund_dispute_handling_ready": True,
        "incident_playbooks_ready": True,
        "pricing_optimisation_review_ready": True,
        "sales_process_refinement_ready": True,
        "backend_update_allowance_preserved": True,
        "owner_approval_required_for_refunds_disputes_and_pricing_changes": True,
        "owner_approval_required_for_enterprise_terms": True,
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "commercial_domains": [
            "client_onboarding",
            "customer_support",
            "refund_dispute_handling",
            "incident_playbooks",
            "pricing_optimisation",
            "sales_process_refinement",
            "backend_update_readiness",
        ],
        "commercial_rules": [
            "Every paid client must be activated through the governed onboarding flow.",
            "Client package, agent selection, billing state, and activation status must be checked before live use.",
            "Refunds, disputes, pricing changes, and enterprise terms require owner approval.",
            "Support issues should be classified by severity, customer impact, billing impact, and technical cause.",
            "Incidents must preserve audit records and avoid exposing credentials or internal logic.",
            "Pricing optimisation may be recommended but cannot change live pricing without owner approval.",
            "Sales process refinements must not make unsupported claims or expose backend configuration.",
        ],
        "operational_sequences": {
            "onboarding": [
                "confirm_payment_or_enterprise_approval",
                "confirm_package_entitlement",
                "confirm_selected_agents",
                "send_activation_or_access_instructions",
                "verify_client_login",
                "verify_business_profile",
                "verify_integrations_if_required",
                "run_first_governed_execution",
            ],
            "support": [
                "capture_issue",
                "classify_severity",
                "check_client_package_and_status",
                "check_recent_execution_or_billing_events",
                "respond_with_customer_safe_update",
                "escalate_to_owner_if_high_risk",
                "record_resolution",
            ],
            "refund_dispute": [
                "capture_request",
                "confirm_billing_record",
                "review_terms_and_usage",
                "owner_review_required",
                "execute_approved_action_only",
                "record_audit_note",
            ],
            "incident": [
                "identify_affected_area",
                "pause_or_restrict_impacted_operation_if_needed",
                "preserve_logs",
                "notify_owner",
                "apply_rollback_or mitigation",
                "confirm_recovery",
                "record_incident_summary",
            ],
            "pricing_optimisation": [
                "collect_conversion_data",
                "collect churn_or_objection_patterns",
                "review_package_mix",
                "recommend_adjustment",
                "owner_approval_required_before_change",
            ],
            "sales_process_refinement": [
                "review_lead_source",
                "review_demo_completion",
                "review_objections",
                "refine_offer_copy",
                "refine_follow_up_sequence",
                "preserve_customer_safe_claims",
            ],
        },
        "verified_at": _now(),
    }


def get_client_safe_post_launch_commercial_operations_sops() -> Dict[str, Any]:
    status = get_post_launch_commercial_operations_sops()

    return {
        "success": status["success"],
        "track": status["track"],
        "layer": status["layer"],
        "status": status["status"],
        "production_launch_matrix_complete": status["production_launch_matrix_complete"],
        "commercial_operations_sops_enabled": status["commercial_operations_sops_enabled"],
        "onboarding_sop_ready": status["onboarding_sop_ready"],
        "customer_support_sop_ready": status["customer_support_sop_ready"],
        "refund_dispute_handling_ready": status["refund_dispute_handling_ready"],
        "incident_playbooks_ready": status["incident_playbooks_ready"],
        "credential_values_exposed": False,
        "external_actions_performed": False,
        "commercial_domains": [
            "client_onboarding",
            "customer_support",
            "refund_dispute_handling",
            "incident_response",
        ],
        "verified_at": status["verified_at"],
    }
'''

DOC_CONTENT = r'''# Post-Launch Commercial Operations SOPs

## Purpose

This document locks the commercial operations layer after the completed Final Production Launch Matrix and the post-launch infrastructure scaling readiness layer.

The platform is production-release ready. These SOPs govern day-to-day customer operations, support, refunds, disputes, sales, onboarding, pricing review, and incident handling.

---

## 1. Client Onboarding SOP

### Goal

Move a paid client from purchase or approved enterprise agreement into safe, governed platform use.

### Sequence

1. Confirm payment or approved enterprise access.
2. Confirm selected package and entitlement.
3. Confirm selected agents.
4. Confirm activation or access instructions were sent.
5. Confirm client login works.
6. Confirm business profile has been completed.
7. Confirm required integrations where applicable.
8. Run the first governed execution.
9. Confirm deliverable visibility in the client workspace.
10. Record onboarding completion.

### Rules

- Do not activate unpaid client access unless owner-approved.
- Do not expose internal configuration or prompts.
- Do not let clients change selected agents after activation unless owner/admin approves.
- Owner/admin remains unrestricted for internal use.

---

## 2. Customer Support SOP

### Goal

Provide structured support without exposing internal systems or credentials.

### Sequence

1. Capture issue.
2. Classify severity.
3. Check client package/status.
4. Check recent billing/execution events.
5. Provide customer-safe update.
6. Escalate high-risk issue to owner.
7. Record resolution.

### Severity

- Low: cosmetic, wording, minor UX issue.
- Medium: workflow confusion, failed non-critical execution.
- High: billing issue, blocked client execution, repeated failures.
- Critical: security, data exposure, payment impact, system outage.

### Rules

- Never expose credentials, prompts, internal routing, governance internals, or proprietary architecture.
- Keep client communication customer-safe.
- Escalate security/billing/high-risk issues.

---

## 3. Refund and Dispute Handling SOP

### Goal

Handle billing issues consistently and protect revenue.

### Sequence

1. Capture refund or dispute request.
2. Confirm billing record.
3. Review usage and subscription terms.
4. Escalate to owner for decision.
5. Execute only approved refund/dispute action.
6. Record audit note.

### Rules

- Refunds and disputes require owner approval.
- Pricing exceptions require owner approval.
- Enterprise contract terms require owner approval.
- Do not promise refunds before review.

---

## 4. Incident Playbook

### Goal

Respond to technical, billing, provider, security, or customer-impacting incidents.

### Sequence

1. Identify affected area.
2. Classify impact and severity.
3. Preserve logs.
4. Notify owner.
5. Pause/restrict affected operation if needed.
6. Apply rollback or mitigation.
7. Confirm recovery.
8. Record incident summary.

### Incident Categories

- Provider failure
- Billing failure
- Client execution failure
- Integration failure
- Security/governance alert
- Data visibility issue
- Frontend/backend route issue

### Rules

- Security and billing incidents escalate immediately.
- Do not expose credentials or internal system details in customer updates.
- Use rollback notes for backend changes.
- Preserve audit trail.

---

## 5. Pricing Optimisation SOP

### Goal

Improve conversion and revenue without uncontrolled price changes.

### Sequence

1. Collect conversion data.
2. Review objections and lost leads.
3. Review package mix.
4. Compare support burden by package.
5. Recommend pricing/package adjustment.
6. Owner approval required before live pricing change.

### Rules

- AI may recommend price changes.
- Owner must approve price changes.
- No autonomous pricing updates.

---

## 6. Sales Process Refinement SOP

### Goal

Improve demo-to-close and signup conversion.

### Sequence

1. Review lead source.
2. Review demo completion.
3. Review objections.
4. Refine offer copy.
5. Refine follow-up sequence.
6. Keep claims customer-safe.
7. Record sales learnings.

### Rules

- Do not make unsupported claims.
- Do not promise unavailable integrations/providers.
- Do not expose backend/internal logic.
- Enterprise promises require owner approval.

---

## 7. Backend Update Allowance

### Goal

Allow future backend updates safely after launch.

### Rules

- Backend updates are allowed after launch.
- High-risk backend changes require owner approval.
- Production schema/migration changes require backup first.
- Every backend update requires test evidence.
- Every backend update requires rollback awareness.
- Never expose credentials or proprietary internals.

## Status

POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_READY
'''

TEST_CONTENT = r'''from pathlib import Path
import importlib.util
import py_compile

ROOT = Path.cwd()

runtime_file = ROOT / "backend" / "app" / "runtime" / "post_launch_commercial_operations_sops.py"
main_file = ROOT / "backend" / "app" / "main.py"
doc_file = ROOT / "docs" / "post-launch-commercial-operations-sops.md"

required_files = [runtime_file, main_file, doc_file]

for path in required_files:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

py_compile.compile(str(runtime_file), doraise=True)

spec = importlib.util.spec_from_file_location(
    "post_launch_commercial_operations_sops",
    runtime_file,
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

status = module.get_post_launch_commercial_operations_sops()
client_status = module.get_client_safe_post_launch_commercial_operations_sops()

required_true_flags = [
    "production_launch_matrix_complete",
    "commercial_operations_sops_enabled",
    "onboarding_sop_ready",
    "customer_support_sop_ready",
    "refund_dispute_handling_ready",
    "incident_playbooks_ready",
    "pricing_optimisation_review_ready",
    "sales_process_refinement_ready",
    "backend_update_allowance_preserved",
    "owner_approval_required_for_refunds_disputes_and_pricing_changes",
    "owner_approval_required_for_enterprise_terms",
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
    "client_onboarding",
    "customer_support",
    "refund_dispute_handling",
    "incident_playbooks",
    "pricing_optimisation",
    "sales_process_refinement",
    "backend_update_allowance_preserved",
    "owner_approval_required_for_refunds_disputes_and_pricing_changes",
    "credential_values_exposed",
    "external_actions_performed",
]

combined_text = runtime_text + "\n" + main_text + "\n" + doc_text

for marker in required_markers:
    if marker not in combined_text:
        raise AssertionError(f"Missing marker: {marker}")

route_markers = [
    "/post-launch/commercial-operations-sops",
    "/admin/post-launch/commercial-operations-sops",
    "get_post_launch_commercial_operations_sops",
]

for marker in route_markers:
    if marker not in main_text:
        raise AssertionError(f"Missing backend route marker: {marker}")

print("POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_PASSED")
'''

MAIN_ROUTE_BLOCK = r'''
# POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_START
try:
    from backend.app.runtime.post_launch_commercial_operations_sops import (
        get_client_safe_post_launch_commercial_operations_sops,
        get_post_launch_commercial_operations_sops,
    )

    @app.get("/post-launch/commercial-operations-sops")
    async def post_launch_commercial_operations_sops():
        return get_client_safe_post_launch_commercial_operations_sops()

    @app.get("/admin/post-launch/commercial-operations-sops")
    async def admin_post_launch_commercial_operations_sops():
        return get_post_launch_commercial_operations_sops()

except Exception as post_launch_commercial_operations_sops_error:
    @app.get("/post-launch/commercial-operations-sops")
    async def post_launch_commercial_operations_sops_unavailable():
        return {
            "success": False,
            "layer": "commercial_operations_sops",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_commercial_operations_sops_error),
        }

    @app.get("/admin/post-launch/commercial-operations-sops")
    async def admin_post_launch_commercial_operations_sops_unavailable():
        return {
            "success": False,
            "layer": "commercial_operations_sops",
            "status": "unavailable",
            "credential_values_exposed": False,
            "external_actions_performed": False,
            "error": str(post_launch_commercial_operations_sops_error),
        }
# POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_END
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

    if "POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_START" not in text:
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + MAIN_ROUTE_BLOCK.lstrip(), encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)

    write_file(RUNTIME_FILE, RUNTIME_CONTENT)
    write_file(DOC_FILE, DOC_CONTENT)
    write_file(TEST_FILE, TEST_CONTENT)
    append_main_route_block()

    print("POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Created/updated: {RUNTIME_FILE}")
    print(f"Created/updated: {DOC_FILE}")
    print(f"Created/updated: {TEST_FILE}")
    print(f"Updated: {MAIN_FILE}")


if __name__ == "__main__":
    main()