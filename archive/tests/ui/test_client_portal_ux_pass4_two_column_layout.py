from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS4_TWO_COLUMN_LAYOUT_RESULTS")

checks = {
    "marker": "client_portal_ux_pass4_two_column_layout" in text,
    "two_column_workspace": 'gridTemplateColumns: "repeat(2, minmax(0, 1fr))"' in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
    "active_agents": "Active agents" in text,
    "execution_pipeline": "Execution pipeline" in text,
    "activity": "Activity" in text,
    "actions": "Actions" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS4_TWO_COLUMN_LAYOUT_OK")
