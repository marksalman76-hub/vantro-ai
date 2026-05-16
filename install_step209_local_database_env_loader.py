from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

sitecustomize_file = ROOT / "sitecustomize.py"
checker_file = ROOT / "test_step209_database_env_loader.py"

for file in [sitecustomize_file, checker_file]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step209_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

sitecustomize_file.write_text(r'''
from __future__ import annotations

import os
from pathlib import Path


def _parse_env_line(line: str):
    line = line.strip()

    if not line or line.startswith("#") or "=" not in line:
        return None, None

    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip()

    if not key:
        return None, None

    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        value = value[1:-1]

    return key, value


def _load_env_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        return

    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            key, value = _parse_env_line(line)
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        return


def _load_local_environment() -> None:
    root = Path(__file__).resolve().parent

    candidates = [
        root / ".env",
        root / ".env.local",
        root / ".env.development",
        root / "backend" / ".env",
        root / "backend" / ".env.local",
        root / "backend" / "app" / ".env",
        root / "backend" / "app" / ".env.local",
        root / "apps" / "web" / ".env",
        root / "apps" / "web" / ".env.local",
    ]

    for candidate in candidates:
        _load_env_file(candidate)

    # Resolve common Supabase/Postgres aliases into DATABASE_URL.
    if not os.environ.get("DATABASE_URL"):
        for alias in [
            "SUPABASE_DATABASE_URL",
            "SUPABASE_DB_URL",
            "POSTGRES_DATABASE_URL",
            "POSTGRES_URL",
            "POSTGRES_PRISMA_URL",
            "POSTGRES_URL_NON_POOLING",
        ]:
            value = os.environ.get(alias)
            if value:
                os.environ["DATABASE_URL"] = value
                os.environ["DATABASE_URL_RESOLVED_FROM"] = alias
                break


_load_local_environment()
'''.lstrip(), encoding="utf-8")

checker_file.write_text(r'''
from __future__ import annotations

import os
from pathlib import Path


def mask(value: str | None) -> str:
    if not value:
        return "MISSING"
    if len(value) <= 12:
        return "***"
    return value[:8] + "..." + value[-6:]


root = Path.cwd()

print("STEP_209_DATABASE_ENV_LOADER_CHECK")
print("sitecustomize_exists", (root / "sitecustomize.py").exists())
print("DATABASE_URL_PRESENT", bool(os.getenv("DATABASE_URL")))
print("DATABASE_URL_MASKED", mask(os.getenv("DATABASE_URL")))
print("DATABASE_URL_RESOLVED_FROM", os.getenv("DATABASE_URL_RESOLVED_FROM", "DATABASE_URL_OR_EXISTING_ENV"))

for name in [
    ".env",
    ".env.local",
    "backend/.env",
    "backend/.env.local",
    "backend/app/.env",
    "backend/app/.env.local",
    "apps/web/.env",
    "apps/web/.env.local",
]:
    print(name, (root / name).exists())

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL_missing_after_step209_loader")

print("STEP_209_DATABASE_ENV_LOADER_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(sitecustomize_file), doraise=True)
py_compile.compile(str(checker_file), doraise=True)

print("STEP_209_LOCAL_DATABASE_ENV_LOADER_INSTALLED")
print(f"Created/updated: {sitecustomize_file}")
print(f"Created/updated: {checker_file}")
print("STEP_209_OK")