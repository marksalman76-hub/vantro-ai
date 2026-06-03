from pathlib import Path

checks = {
    "frontend/src/lib/executionStateSync.ts": [
        "persistExecutionState",
        "getExecutionState",
        "mergeExecutionState",
        "client-execution-state.json",
        "execution_state_synchronised",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "persistExecutionState",
        "execution_state_synchronised",
        "execution_state",
    ],
    "frontend/src/app/api/client-latest-deliverable/route.ts": [
        "mergeExecutionState",
        "persistExecutionState",
        "execution_state_synchronised",
    ],
    "frontend/src/app/api/client-execution-matrix/route.ts": [
        "getExecutionState",
        "execution_state_synchronised",
        "Business profile",
        "Deliverable",
        "Review",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW6_EXECUTION_STATE_SYNCHRONISATION_FAILED missing={missing}")

print("ROW6_EXECUTION_STATE_SYNCHRONISATION_PASSED")
