from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS7_COMPACT_AGENTS_INTEGRATIONS_RESULTS")

checks = {
    "marker": "client_portal_ux_pass7_compact_agents_integrations" in text,
    "compact_agent_grid": 'gridTemplateColumns: "280px minmax(0,1fr)"' in text,
    "compact_agent_padding": 'padding: "9px 11px"' in text,
    "compact_integrations": 'gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))"' in text,
    "task_rows": "rows={5}" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS7_COMPACT_AGENTS_INTEGRATIONS_OK")
