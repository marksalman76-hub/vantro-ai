from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS14_ACTIVITY_COMPACT_RESULTS")

checks = {
    "marker": "client_portal_activity_feed_compact_locked" in text,
    "slice_latest_2": "]).slice(0, 2).map((event) => {" in text,
    "compact_padding": "padding: 12" in text,
    "compact_tag_padding": 'padding: "4px 7px"' in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS14_ACTIVITY_COMPACT_OK")
