from pathlib import Path

old = "https://api.trance-formation.com.au"
new = "https://ecommerce-ai-agent-platform-1.onrender.com"

files = [
    "live_ai_media_admin_validation.py",
    "live_admin_auth_header_probe.py",
    "live_route_fingerprint.py",
    "live_route_fingerprint_with_auth.py",
    "check_live_backend_identity.py",
    "check_live_backend_identity_with_auth.py",
]

for name in files:
    path = Path(name)

    if not path.exists():
        print("missing", name)
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")

    if old in text:
        path.write_text(text.replace(old, new), encoding="utf-8")
        print("updated", name)
    else:
        print("no change", name)