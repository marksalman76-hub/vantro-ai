from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, Optional


_SECRET_NAMES = {
    "ADMIN_PLATFORM_TOKEN",
    "JWT_SECRET",
    "SESSION_SECRET",
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "SMTP_PASSWORD",
    "BREVO_API_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
}


@dataclass(frozen=True)
class SecretCheck:
    name: str
    present: bool
    masked: str
    source: str = "environment"


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def require_secret(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required secret is missing: {name}")
    return value


def mask_secret(value: Optional[str]) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "***"
    return f"{value[:3]}...{value[-3:]}"


def redact_text(value: str) -> str:
    if not value:
        return value

    redacted = str(value)

    # Provider/token shapes
    token_patterns = [
        r"sk-[A-Za-z0-9_\-]{20,}",
        r"rk_live_[A-Za-z0-9_\-]{20,}",
        r"whsec_[A-Za-z0-9_\-]{20,}",
        r"AIza[A-Za-z0-9_\-]{20,}",
        r"postgres(?:ql)?://[^\s\"']+",
    ]

    for pattern in token_patterns:
        redacted = re.sub(pattern, "[REDACTED_SECRET]", redacted)

    # Assignment-form secrets, including hyphenated local/test values.
    assignment_names = [
        "ADMIN_PLATFORM_TOKEN",
        "JWT_SECRET",
        "SESSION_SECRET",
        "SECRET_KEY",
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "SMTP_PASSWORD",
        "BREVO_API_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]

    for name in assignment_names:
        redacted = re.sub(
            rf"({name}\s*=\s*)([^\s\"']+)",
            rf"\1[REDACTED_SECRET]",
            redacted,
        )
        redacted = re.sub(
            rf"({name}[\"']?\s*:\s*[\"'])([^\"']+)([\"'])",
            rf"\1[REDACTED_SECRET]\3",
            redacted,
        )

    return redacted


def secret_inventory() -> Dict[str, SecretCheck]:
    inventory: Dict[str, SecretCheck] = {}
    for name in sorted(_SECRET_NAMES):
        value = os.getenv(name)
        inventory[name] = SecretCheck(
            name=name,
            present=bool(value),
            masked=mask_secret(value),
        )
    return inventory


def production_secret_readiness() -> Dict[str, object]:
    inventory = secret_inventory()
    missing = [name for name, check in inventory.items() if not check.present]

    return {
        "success": len(missing) == 0,
        "mode": "env_only_secret_access",
        "secret_values_exposed": False,
        "missing": missing,
        "present_count": len(inventory) - len(missing),
        "total_required": len(inventory),
        "inventory": {
            name: {
                "present": check.present,
                "masked": check.masked,
                "source": check.source,
            }
            for name, check in inventory.items()
        },
    }
