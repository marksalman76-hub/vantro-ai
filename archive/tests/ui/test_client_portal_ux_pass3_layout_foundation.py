from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS3_LAYOUT_FOUNDATION_RESULTS")

checks = {
    "marker": "client_portal_ux_pass3_layout_foundation" in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
    "stable_workspace_grid": 'gridTemplateColumns: "minmax(360px, 1.15fr) minmax(260px, 0.85fr) minmax(260px, 0.75fr)"' in text,
    "stable_secondary_grid": 'gridTemplateColumns: "minmax(360px, 0.9fr) minmax(520px, 1.1fr)"' in text,
    "compact_agent_copy": "Select approved agents and launch governed execution." in text,
    "active_agents_copy": "Active agents" in text,
    "latest_activity_copy": "Latest governed activity" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS3_LAYOUT_FOUNDATION_OK")
