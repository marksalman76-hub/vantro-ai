from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS5_PREMIUM_INPUTS_RESULTS")

checks = {
    "marker": "client_portal_ux_pass5_premium_inputs" in text,
    "agent_selector_width": 'gridTemplateColumns: "320px minmax(0,1fr)"' in text,
    "premium_agent_shadow": "0 10px 30px rgba(37,99,235,0.10)" in text,
    "textarea_minheight": 'minHeight: 120' in text,
    "integration_cards": 'linear-gradient(180deg,#ffffff,#fbfdff)' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS5_PREMIUM_INPUTS_OK")
