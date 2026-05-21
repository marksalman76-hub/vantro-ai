from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS6_AGENTS_INTEGRATIONS_RESULTS")

checks = {
    "marker": "client_portal_ux_pass6_agents_integrations" in text,
    "default_agents_added": '"product_copywriting_agent"' in text and '"crm_ai_agent"' in text,
    "agent_grid_fixed": 'gridTemplateColumns: "minmax(300px, 0.92fr) minmax(360px, 1.08fr)"' in text,
    "integration_pill_grid": 'gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))"' in text,
    "no_black_border": 'border: "1px solid black"' not in text and 'border: "2px solid black"' not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS6_AGENTS_INTEGRATIONS_OK")
