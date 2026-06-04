from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "backend" / "app" / "runtime" / "admin_creative_media_asset_viewer.py"

backup_dir = ROOT / "backups" / f"asset_gateway_backend_domain_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

(backup_dir / "admin_creative_media_asset_viewer.py").write_text(
    TARGET.read_text(encoding="utf-8"),
    encoding="utf-8",
)

text = TARGET.read_text(encoding="utf-8")

old = '''def _backend_base_url() -> str:
    return (
        os.getenv("API_BASE_URL")
        or os.getenv("BACKEND_BASE_URL")
        or os.getenv("PUBLIC_BACKEND_BASE_URL")
        or "https://api.trance-formation.com.au"
    ).rstrip("/")
'''

new = '''def _backend_base_url() -> str:
    value = (
        os.getenv("API_BASE_URL")
        or os.getenv("BACKEND_BASE_URL")
        or os.getenv("PUBLIC_BACKEND_BASE_URL")
        or "https://api.trance-formation.com.au"
    ).rstrip("/")

    if "app.trance-formation.com.au" in value:
        return "https://api.trance-formation.com.au"

    return value
'''

if old not in text:
    raise SystemExit("Expected _backend_base_url block not found. No changes made.")

TARGET.write_text(text.replace(old, new), encoding="utf-8")

print("ASSET_GATEWAY_BACKEND_DOMAIN_FIXED")
print("Updated:", TARGET)
print("Backup:", backup_dir)