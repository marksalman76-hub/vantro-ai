from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS10_BUSINESS_CONTEXT_REFINE_RESULTS")

checks = {
    "marker": "client_portal_ux_pass10_business_context_refine" in text,
    "neutral_heading": "Store business context for tailored AI execution" in text,
    "neutral_description": "market, goals, and operating style" in text,
    "wider_grid": 'gridTemplateColumns: "repeat(8, minmax(150px, 1fr))"' in text,
    "rows_3": "rows={3}" in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS10_BUSINESS_CONTEXT_REFINE_OK")
