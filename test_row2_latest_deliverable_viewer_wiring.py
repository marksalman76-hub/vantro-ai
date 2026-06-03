from pathlib import Path

client_page = Path("frontend/src/app/client/page.tsx")
component = Path("frontend/src/app/client/LatestDeliverableViewer.tsx")
api_route = Path("frontend/src/app/api/client-latest-deliverable/route.ts")

checks = {
    str(client_page): [
        'LatestDeliverableViewer from "./LatestDeliverableViewer"',
        '<LatestDeliverableViewer />',
    ],
    str(component): [
        'Latest deliverable',
        'Client output viewer',
        'has_real_output',
        'Preview latest asset',
        'No real deliverable, output, or generated asset exists yet.',
    ],
    str(api_route): [
        'client_output_truth_checked',
        'has_real_output',
        'Output pending',
        'Completed',
        'cache: "no-store"',
    ],
}

missing = {}
for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW2_LATEST_DELIVERABLE_VIEWER_WIRING_FAILED missing={missing}")

print("ROW2_LATEST_DELIVERABLE_VIEWER_WIRING_PASSED")
