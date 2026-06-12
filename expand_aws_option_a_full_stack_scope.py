from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
MATRIX = ROOT / "AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md"
SAFETY = ROOT / "verify_aws_migration_safety_checkpoint.py"

if not MATRIX.exists():
    raise SystemExit("Missing AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

text = MATRIX.read_text(encoding="utf-8")

section = f"""

---

# Full-Stack AWS Option A Scope Addendum

Updated: {datetime.now().isoformat(timespec="seconds")}

## Correction

AWS Option A migration is not media-only. The production migration must cover the full paid-client platform stack and both portals.

## Full Stack Areas Covered

| Stack area | AWS migration requirement |
|---|---|
| Admin portal | Preserve unrestricted owner/admin authority, full diagnostics, provider details, infrastructure visibility, job controls, retries, refunds, credit assignment, and full audit visibility. |
| Client portal | Preserve client-safe status, package/credit governance, approvals, privacy-safe outputs, usable assets, billing visibility, and support flows. |
| Media generation | Move paid-client media execution to durable API + queue + worker + object storage. |
| Agent execution | Route execution through durable job records, provider events, audit logs, and portal-safe status views. |
| Billing and credits | Durable credit ledger, package enforcement, usage estimates, provider-cost tracking, refunds, and admin credit assignment. |
| Package enforcement | Client entitlement checks before paid execution; admin owner bypass preserved. |
| Approvals | Owner approval controls for governed spend/actions; client request visibility without internal leakage. |
| Provider execution | Provider adapters run server-side only; provider secrets are never exposed to frontend or client views. |
| Creative assets | Durable asset storage with S3-backed delivery and portal-safe metadata. |
| Client uploads | Durable uploads, privacy-safe handling, uploaded likeness consent, and access control. |
| Generated sites | Durable generated-site records/assets and deployment evidence. |
| Integrations | Durable integration connection state, health checks, and client-safe connection status. |
| Execution evidence | Store outputs, provider events, timestamps, screenshots/files when relevant, and audit history. |
| Learning/memory/governance | Preserve governed learning, memory rules, admin visibility, and client-safe boundaries. |
| Security/session handling | Portal-specific authentication, authorization, session hardening, and no secret leakage. |
| Observability | CloudWatch logs, metrics, incident readiness, dead-letter queue visibility, and admin-only diagnostics. |
| Support flows | Client support requests and admin handling must remain functional after migration. |

## Portal Authority Model

| Capability | Admin / owner portal | Client portal |
|---|---|---|
| Execute jobs | Unrestricted owner execution | Governed by package, credits, approvals |
| View provider diagnostics | Full visibility | Hidden |
| View provider secrets/config | Never raw secrets, but admin diagnostics allowed | Hidden |
| Retry/requeue/cancel jobs | Allowed | Limited/client-safe request flow only |
| Assign credits | Allowed | Not allowed |
| Spend approvals | Owner/admin controls | Request/status only |
| Refunds | Admin controls | Request/status only |
| Uploaded likeness | Full admin audit visibility | Consent-based client control |
| Assets | Full asset visibility | Own/client-safe assets only |
| Infrastructure status | Full | Hidden or simplified status only |
| Audit logs | Full | Own/client-safe history only |

## Non-Negotiable Migration Rule

Do not migrate media in isolation in a way that breaks or ignores the wider stack.

Every AWS-backed production service must preserve:
- admin/client authority separation
- package and credit enforcement
- owner/admin unrestricted operations
- provider secret protection
- durable job/status/asset records
- auditability
- client-safe output visibility
"""

if "Full-Stack AWS Option A Scope Addendum" not in text:
    MATRIX.write_text(text.rstrip() + section + "\n", encoding="utf-8")
else:
    print("Matrix already contains full-stack addendum")

if SAFETY.exists():
    safety = SAFETY.read_text(encoding="utf-8")
    old = '''        "not ecommerce-only",'''
    new = '''        "not ecommerce-only",
        "Full-Stack AWS Option A Scope Addendum",
        "Admin portal",
        "Client portal",
        "Portal Authority Model",
        "Billing and credits",
        "Package enforcement",
        "Provider execution",
        "Security/session handling",'''
    if old in safety and "Full-Stack AWS Option A Scope Addendum" not in safety:
        safety = safety.replace(old, new)
        SAFETY.write_text(safety, encoding="utf-8")
    else:
        print("Safety checkpoint already updated or marker not found")

print("AWS_OPTION_A_FULL_STACK_SCOPE_EXPANDED")
print(f"Updated: {MATRIX}")
print(f"Updated: {SAFETY}")