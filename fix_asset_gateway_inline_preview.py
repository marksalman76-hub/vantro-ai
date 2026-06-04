from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "backend" / "app" / "main.py"

backup_dir = ROOT / "backups" / f"asset_gateway_inline_preview_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

(backup_dir / "main.py").write_text(
    TARGET.read_text(encoding="utf-8"),
    encoding="utf-8",
)

text = TARGET.read_text(encoding="utf-8")

old = '''        serve_file_path = result.get("serve_file_path")
        if serve_file_path:
            filename = result.get("filename")
            content_type = result.get("content_type") or "application/octet-stream"
            if filename:
                return FileResponse(path=serve_file_path, media_type=content_type, filename=filename)
            return FileResponse(path=serve_file_path, media_type=content_type)
'''

new = '''        serve_file_path = result.get("serve_file_path")
        if serve_file_path:
            filename = result.get("filename")
            content_type = result.get("content_type") or "application/octet-stream"

            response = FileResponse(
                path=serve_file_path,
                media_type=content_type,
                filename=filename if delivery_type == "download" else None,
            )

            if delivery_type == "preview":
                response.headers["Content-Disposition"] = "inline"

            return response
'''

if old not in text:
    raise SystemExit("Expected FileResponse block not found. No changes made.")

TARGET.write_text(text.replace(old, new), encoding="utf-8")

print("ASSET_GATEWAY_INLINE_PREVIEW_FIXED")
print("Updated:", TARGET)
print("Backup:", backup_dir)