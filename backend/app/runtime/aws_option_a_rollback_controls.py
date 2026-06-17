from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any, Dict, Mapping, Optional


AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG = "AWS_OPTION_A_KILL_SWITCH_ENABLED"
AWS_OPTION_A_FORCE_COMPATIBILITY_FALLBACK_FLAG = "AWS_OPTION_A_FORCE_COMPATIBILITY_FALLBACK"
AWS_OPTION_A_ROLLBACK_REASON_FLAG = "AWS_OPTION_A_ROLLBACK_REASON"

TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}

SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "database_url",
    "password",
    "private_key",
    "provider_api_key",
    "rds_password",
    "secret",
    "stripe_secret_key",
    "token",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def enabled(value: Any) -> bool:
    return clean_text(value, 80).lower() in TRUE_VALUES


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if isinstance(item, bool):
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


def sanitize_rollback_reason(value: Any, limit: int = 240) -> str:
    text = clean_text(value, limit * 2)
    if not text:
        return ""
    text = re.sub(r"arn:aws:[^\s,;]+", "[redacted-arn]", text, flags=re.IGNORECASE)
    text = re.sub(r"https?://[^\s,;]+", "[redacted-url]", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d{12,}\b", "[redacted-id]", text)
    text = re.sub(r"postgres(?:ql)?://[^\s,;]+", "[redacted-database-url]", text, flags=re.IGNORECASE)
    text = re.sub(
        r"(?i)\b(?:[a-z0-9]+[_-])*(?:aws_access_key_id|aws_secret_access_key|aws_session_token|api[_-]?key|authorization|bearer|credential|database_url|password|private_key|provider[_-]?api[_-]?key|rds_password|secret|stripe[_-]?secret[_-]?key|token)\b\s*[:=]?\s*[^\s,;]*",
        "[redacted-secret-marker]",
        text,
    )
    text = re.sub(
        r"(?i)\b(?:[a-z0-9]+[_-])*(?:aws_access_key_id|aws_secret_access_key|aws_session_token|api[_-]?key|authorization|bearer|credential|database_url|password|private_key|provider[_-]?api[_-]?key|rds_password|secret|stripe[_-]?secret[_-]?key|token)\b",
        "[redacted-secret-marker]",
        text,
    )
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def build_client_safe_rollback_view(control: Mapping[str, Any]) -> Dict[str, Any]:
    active = bool(control.get("rollback_control_active"))
    return {
        "status": "current_runtime_active" if active else "normal_processing_available",
        "processing_mode": "current_production_runtime",
        "message": "This request will use the current production runtime path.",
        "external_calls_started": False,
        "paid_provider_calls_started": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "sensitive_values_exposed": False,
        "internal_config_exposed": False,
        "customer_safe": True,
    }


def build_aws_option_a_rollback_control_decision(
    *,
    env: Optional[Mapping[str, Any]] = None,
    route_kind: str = "acceptance",
    route_intent: bool = False,
    route_execution_allowed: bool = False,
    selected_runtime_path: str = "",
    route_mode: str = "",
) -> Dict[str, Any]:
    env = dict(env or {})
    kill_switch_active = enabled(env.get(AWS_OPTION_A_KILL_SWITCH_ENABLED_FLAG))
    force_compatibility = enabled(env.get(AWS_OPTION_A_FORCE_COMPATIBILITY_FALLBACK_FLAG))
    active = kill_switch_active or force_compatibility
    reason_sanitized = sanitize_rollback_reason(env.get(AWS_OPTION_A_ROLLBACK_REASON_FLAG))
    aws_route_blocked = bool(route_intent and active)
    compatibility_selected = bool(aws_route_blocked)
    base = {
        "boundary": "aws18_rollback_control_boundary",
        "status": (
            "aws_option_a_kill_switch_active"
            if kill_switch_active
            else (
                "aws_option_a_compatibility_fallback_forced"
                if force_compatibility
                else "aws_option_a_rollback_control_clear"
            )
        ),
        "route_kind": clean_text(route_kind, 80),
        "route_mode": clean_text(route_mode, 120),
        "selected_runtime_path_before_rollback": clean_text(selected_runtime_path, 180),
        "selected_runtime_path_after_rollback": (
            "existing_compatibility_runtime_path"
            if compatibility_selected
            else clean_text(selected_runtime_path, 180)
        ),
        "rollback_control_active": active,
        "kill_switch_active": kill_switch_active,
        "force_compatibility_fallback": force_compatibility,
        "rollback_reason_present": bool(reason_sanitized),
        "rollback_reason_sanitized": reason_sanitized,
        "aws_route_blocked_by_rollback": aws_route_blocked,
        "compatibility_fallback_selected": compatibility_selected,
        "route_execution_allowed_before_rollback": bool(route_execution_allowed),
        "route_execution_allowed_after_rollback": bool(route_execution_allowed and not aws_route_blocked),
        "admin_override_available": False,
        "client_bypass_allowed": False,
        "created_at": utc_now(),
        "live_routes_switched": False,
        "rds_write_attempted": False,
        "db_connection_attempted": False,
        "migration_attempted": False,
        "sqs_send_attempted": False,
        "s3_upload_attempted": False,
        "secret_fetch_attempted": False,
        "aws_call_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "billing_mutation_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    }
    base["admin_safe_view"] = {
        "boundary": base["boundary"],
        "status": base["status"],
        "rollback_control_active": base["rollback_control_active"],
        "kill_switch_active": base["kill_switch_active"],
        "force_compatibility_fallback": base["force_compatibility_fallback"],
        "rollback_reason_present": base["rollback_reason_present"],
        "rollback_reason_sanitized": base["rollback_reason_sanitized"],
        "aws_route_blocked_by_rollback": base["aws_route_blocked_by_rollback"],
        "compatibility_fallback_selected": base["compatibility_fallback_selected"],
        "selected_runtime_path_after_rollback": base["selected_runtime_path_after_rollback"],
        "rds_write_attempted": False,
        "sqs_send_attempted": False,
        "provider_call_attempted": False,
        "stripe_call_attempted": False,
        "credit_mutation_attempted": False,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
        "customer_safe": True,
    }
    base["client_safe_view"] = build_client_safe_rollback_view(base)
    return redact_secret_values(base)
