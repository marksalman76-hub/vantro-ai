import os
from pathlib import Path

ROOT = Path.cwd()
ENV_FILES = [
    ROOT / ".env.local",
    ROOT / "frontend" / ".env.local",
]

for env_file in ENV_FILES:
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            clean = line.strip()
            if not clean or clean.startswith("#") or "=" not in clean:
                continue
            key, value = clean.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")

required = {
    "BACKEND_URL": bool(os.getenv("BACKEND_URL")),
    "NEXT_PUBLIC_BACKEND_URL": bool(os.getenv("NEXT_PUBLIC_BACKEND_URL")),
    "PORTAL_ACCESS_CODE": bool(os.getenv("PORTAL_ACCESS_CODE")),
}

checks = {
    "backend_url_present": required["BACKEND_URL"],
    "next_public_backend_url_present": required["NEXT_PUBLIC_BACKEND_URL"],
    "portal_access_code_present": required["PORTAL_ACCESS_CODE"],
    "backend_url_render_target": "onrender.com" in (os.getenv("BACKEND_URL") or ""),
    "next_public_backend_url_render_target": "onrender.com" in (os.getenv("NEXT_PUBLIC_BACKEND_URL") or ""),
    "secret_values_not_printed": True,
}

print("STEP_243_FRONTEND_ENV_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("frontend_env_presence_only", required)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_243_FRONTEND_ENV_LOCK_OK")
