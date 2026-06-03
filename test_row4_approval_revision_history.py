from pathlib import Path

checks = {
    "frontend/src/lib/approvalRevisionHistory.ts": [
        "persistApprovalRevisionEvent",
        "getApprovalRevisionHistory",
        "approval-history",
        "approval-revision-history.json",
    ],
    "frontend/src/app/api/client-review-action/route.ts": [
        "persistApprovalRevisionEvent",
        "approval_revision_event_saved",
        "approval_revision_event_id",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "approval_revision_history",
        "latest_review_action",
        "getApprovalRevisionHistory",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")

    absent = [needle for needle in needles if needle not in text]

    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(
        f"ROW4_APPROVAL_REVISION_HISTORY_FAILED missing={missing}"
    )

print("ROW4_APPROVAL_REVISION_HISTORY_PASSED")
