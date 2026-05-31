from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS17_RESPONSIVE_MOTION_RESULTS")

checks = {
    "marker": "client_portal_responsive_motion_locked" in text,
    "responsive_css": "client_portal_responsive_motion_css" in text,
    "media_1180": "@media (max-width: 1180px)" in text,
    "media_760": "@media (max-width: 760px)" in text,
    "transition": "transition:" in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS17_RESPONSIVE_MOTION_OK")
