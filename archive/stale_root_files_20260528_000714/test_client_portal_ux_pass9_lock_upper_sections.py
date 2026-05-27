from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS9_LOCK_UPPER_SECTIONS_RESULTS")

checks = {
    "lock_marker": "client_portal_upper_sections_locked_pre_bottom_rebuild" in text,
    "business_one_line_grid": 'gridTemplateColumns: "repeat(8, minmax(130px, 1fr))"' in text,
    "compact_rows": "rows={2}" in text,
    "compact_padding": 'padding: "11px 12px"' in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS9_LOCK_UPPER_SECTIONS_OK")
