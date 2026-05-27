from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS8_COMPACT_WORKSPACE_PILLS_RESULTS")

checks = {
    "marker": "client_portal_ux_pass8_compact_workspace_pills" in text,
    "integration_pills": "+ Add integration" in text and "Connected systems" in text,
    "compact_agent_grid": 'gridTemplateColumns: "245px minmax(0,1fr)"' in text,
    "task_rows": "rows={4}" in text,
    "bubble_fix": "minWidth: 30" in text and "borderRadius: 999" in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS8_COMPACT_WORKSPACE_PILLS_OK")
