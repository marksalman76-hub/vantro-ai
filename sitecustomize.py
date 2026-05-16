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
