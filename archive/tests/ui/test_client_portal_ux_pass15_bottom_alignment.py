from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS15_BOTTOM_ALIGNMENT_RESULTS")

checks = {
    "marker": "client_portal_bottom_cards_aligned_locked" in text,
    "stretch_grid": 'alignItems: "stretch"' in text,
    "fixed_lower_height": 'height: 560' in text,
    "inner_scroll": 'maxHeight: 430' in text and 'overflowY: "auto"' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS15_BOTTOM_ALIGNMENT_OK")
