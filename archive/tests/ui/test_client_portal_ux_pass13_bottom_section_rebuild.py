from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")

text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS13_BOTTOM_SECTION_REBUILD_RESULTS")

checks = {
    "marker": "client_portal_bottom_section_rebuild_locked" in text,
    "preview_button": "Preview" in text,
    "open_deliverable_button": "Open deliverable" in text,
    "compressed_padding": 'padding: "10px 14px"' in text,
    "compressed_modal_radius": 'borderRadius: 22' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS13_BOTTOM_SECTION_REBUILD_OK")
