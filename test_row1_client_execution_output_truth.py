from pathlib import Path

route = Path("frontend/src/app/api/delegated-workforce-execution/route.ts")
text = route.read_text(encoding="utf-8")

required = [
    "hasRealClientOutput",
    "normaliseClientExecutionTruth",
    "client_output_truth_checked",
    "No real deliverable, output, or generated asset was returned.",
    "Output pending",
    "Completed",
    "cache: \"no-store\"",
]

missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"ROW1_CLIENT_EXECUTION_OUTPUT_TRUTH_FAILED missing={missing}")

print("ROW1_CLIENT_EXECUTION_OUTPUT_TRUTH_PASSED")
