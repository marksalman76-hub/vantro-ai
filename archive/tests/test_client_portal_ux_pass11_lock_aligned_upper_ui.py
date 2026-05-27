from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS11_LOCK_ALIGNED_UPPER_UI_RESULTS")

checks = {
    "lock_marker": "client_portal_aligned_upper_ui_locked" in text,
    "new_heading": "Business context for tailored AI execution" in text,
    "old_heading_removed": "Store business context for tailored AI execution" not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS11_LOCK_ALIGNED_UPPER_UI_OK")
