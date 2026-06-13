from pathlib import Path
from datetime import datetime
import re

p = Path("backend/app/main.py")
s = p.read_text(encoding="utf-8")

backup_dir = Path("backups") / f"safe_runway_key_diagnostics_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "backend_app_main.py").write_text(s, encoding="utf-8")

route = r'''

# SAFE_RUNWAY_KEY_DIAGNOSTICS_V1
@app.get("/admin/runway-key-diagnostics")
def admin_runway_key_diagnostics(
    x_actor_role: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> Dict[str, object]:
    import hashlib
    import os

    if not _admin_media_job_authorized(
        x_actor_role=x_actor_role,
        x_admin_token=x_admin_token,
        authorization=authorization,
    ):
        return {
            "success": False,
            "error": "admin_only",
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    candidate_names = [
        "RUNWAY_API_KEY",
        "RUNWAYML_API_KEY",
        "RUNWAY_TOKEN",
        "RUNWAYML_TOKEN",
        "RUNWAY_API_TOKEN",
    ]

    keys = []
    for name in candidate_names:
        value = str(os.getenv(name) or "").strip()
        if value:
            digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
            keys.append({
                "env_name": name,
                "present": True,
                "length": len(value),
                "sha256_prefix": digest[:12],
                "starts_with": value[:4] + "***" if len(value) >= 4 else "***",
            })
        else:
            keys.append({
                "env_name": name,
                "present": False,
                "length": 0,
            })

    return {
        "success": True,
        "status": "runway_key_metadata_only",
        "keys": keys,
        "note": "No credential values are exposed. Compare sha256_prefix/length with the intended key locally or in Render.",
        "customer_safe": True,
        "credential_values_exposed": False,
    }
'''

if "/admin/runway-key-diagnostics" not in s:
    s = s.rstrip() + "\n" + route + "\n"

p.write_text(s, encoding="utf-8")

print("SAFE_RUNWAY_KEY_DIAGNOSTICS_INSTALLED")
print(f"Backup: {backup_dir}")
print("Updated: backend/app/main.py")