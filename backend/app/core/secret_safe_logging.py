from __future__ import annotations

from typing import Any

from backend.app.core.secure_runtime_config import redact_text


def redact_for_log(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {key: redact_for_log(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_for_log(item) for item in value]
    return value


def safe_log_event(event: dict) -> dict:
    return redact_for_log(event)
