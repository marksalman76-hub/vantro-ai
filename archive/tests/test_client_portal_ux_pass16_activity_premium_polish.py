from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS16_ACTIVITY_PREMIUM_POLISH_RESULTS")

checks = {
    "marker": "client_portal_activity_premium_polish_locked" in text,
    "compact_padding": 'padding: "10px 12px"' in text,
    "compact_pills": 'padding: "3px 6px"' in text,
    "softened_borders": 'rgba(15, 23, 42, 0.08)' in text,
    "compact_timestamp": 'fontSize: 10.5' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS16_ACTIVITY_PREMIUM_POLISH_OK")
