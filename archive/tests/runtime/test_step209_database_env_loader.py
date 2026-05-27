from __future__ import annotations

import os
from pathlib import Path

import sitecustomize  # force local env loader


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
print(".env.local", (root / ".env.local").exists())

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL_missing_after_step209_loader")

print("STEP_209_DATABASE_ENV_LOADER_OK")