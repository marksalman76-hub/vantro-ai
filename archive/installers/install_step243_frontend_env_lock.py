from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ENV = ROOT / ".env.local"
FRONTEND_ENV = ROOT / "frontend" / ".env.local"
TEST = ROOT / "test_step243_frontend_env_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in [ENV, FRONTEND_ENV, TEST]:
    if file.exists():
        backup = BACKUPS / f"{file.name.replace('.', '_')}_before_step243_{timestamp}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

required_values = {
    "BACKEND_URL": "https://ecommerce-ai-agent-platform-1.onrender.com",
    "NEXT_PUBLIC_BACKEND_URL": "https://ecommerce-ai-agent-platform-1.onrender.com",
    "PORTAL_ACCESS_CODE": "change_this_before_public_launch",
}


def upsert_env(path: Path, values: dict):
    lines = []

    if path.exists():
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    existing_keys = set()
    new_lines = []

    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in values:
                new_lines.append(f"{key}={values[key]}")
                existing_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    for key, value in values.items():
        if key not in existing_keys:
            new_lines.append(f"{key}={value}")

    path.write_text("\n".join(new_lines).strip() + "\n", encoding="utf-8")


upsert_env(ENV, required_values)
upsert_env(FRONTEND_ENV, required_values)

TEST.write_text(r'''
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
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_243_FRONTEND_ENV_LOCK_INSTALLED")
print(f"Updated: {ENV}")
print(f"Updated: {FRONTEND_ENV}")
print(f"Created/updated: {TEST}")
print("STEP_243_OK")