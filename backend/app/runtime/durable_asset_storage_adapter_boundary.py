from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import mimetypes
import uuid

from backend.app.runtime.aws_option_a_runtime_contract import aws_option_a_readiness


SECRET_KEY_MARKERS = (
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "password",
    "private_key",
    "provider_api_key",
    "runway_api_key",
    "elevenlabs_api_key",
    "secret",
    "stripe_secret_key",
    "token",
)

SAFE_BOOLEAN_MARKER_KEYS = {
    "credential_values_exposed",
    "provider_secret_values_visible",
    "requires_aws_credentials_now",
}

SUPPORTED_SOURCE_TYPES = {
    "upload",
    "generated",
    "provider_output",
    "composed_output",
    "document",
    "site",
    "evidence",
    "support_attachment",
    "thumbnail",
    "preview",
    "caption",
    "transcript",
    "audio",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "asset") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def clean_text(value: Any, limit: int = 1000) -> str:
    return str(value or "").strip()[:limit]


def clean_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in {"1", "true", "yes", "on", "enabled"}:
        return True
    if text in {"0", "false", "no", "off", "disabled"}:
        return False
    return default


def clean_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(float(value)))
    except Exception:
        return default


def first_value(payload: Mapping[str, Any], keys: Iterable[str], default: Any = "") -> Any:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return default


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if key_l in SAFE_BOOLEAN_MARKER_KEYS:
                cleaned[key] = item
            elif any(marker in key_l for marker in SECRET_KEY_MARKERS):
                cleaned[key] = "[redacted]"
            else:
                cleaned[key] = redact_secret_values(item)
        return cleaned
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    return value


def has_unredacted_secret_value(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            key_l = str(key).lower()
            if key_l in SAFE_BOOLEAN_MARKER_KEYS:
                continue
            if any(marker in key_l for marker in SECRET_KEY_MARKERS) and item != "[redacted]":
                return True
            if has_unredacted_secret_value(item):
                return True
        return False
    if isinstance(value, list):
        return any(has_unredacted_secret_value(item) for item in value)
    return False


def content_type_for_path(path: str, fallback: str = "application/octet-stream") -> str:
    return mimetypes.guess_type(path)[0] or fallback


def file_size_if_available(path: str) -> int:
    try:
        candidate = Path(path)
        if candidate.exists() and candidate.is_file():
            return candidate.stat().st_size
    except Exception:
        pass
    return 0


@dataclass(frozen=True)
class CanonicalAssetReference:
    asset_id: str
    customer_id: str = ""
    account_id: str = ""
    tenant_id: str = ""
    job_id: str = ""
    asset_type: str = "asset"
    media_type: str = ""
    source_type: str = "generated"
    local_path: str = ""
    storage_backend: str = "local_reference"
    storage_key: str = ""
    future_s3: Dict[str, Any] = field(default_factory=dict)
    public_url: str = ""
    client_safe_url: str = ""
    admin_url: str = ""
    content_type: str = "application/octet-stream"
    size_bytes: int = 0
    checksum_sha256: str = ""
    created_at: str = field(default_factory=utc_now)
    created_by_role: str = "system"
    client_visible: bool = True
    admin_visible: bool = True
    retention: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)
    provider_source_metadata: Dict[str, Any] = field(default_factory=dict)
    diagnostics_visibility_rules: Dict[str, Any] = field(default_factory=dict)
    customer_safe: bool = True
    credential_values_exposed: bool = False
    internal_config_exposed: bool = False
    aws_s3_required: bool = False
    s3_upload_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def normalise_source_type(value: Any) -> str:
    source_type = clean_text(value or "generated", 80).lower()
    return source_type if source_type in SUPPORTED_SOURCE_TYPES else "generated"


def build_future_s3_metadata(payload: Mapping[str, Any], source_type: str, asset_id: str) -> Dict[str, Any]:
    preferred_bucket = clean_text(payload.get("s3_bucket") or payload.get("future_s3_bucket"), 240)
    preferred_key = clean_text(payload.get("s3_key") or payload.get("future_s3_key"), 1000)
    return {
        "target_backend": "aws_s3",
        "s3_bucket": preferred_bucket,
        "s3_key": preferred_key or f"{source_type}/{asset_id}",
        "signed_url_strategy": "portal_authorized_presigned_url",
        "s3_upload_enabled": False,
        "requires_aws_credentials_now": False,
    }


def build_asset_reference(payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    payload = dict(payload or {})
    asset_id = clean_text(payload.get("asset_id") or safe_id("asset_ref"), 180)
    source_type = normalise_source_type(payload.get("source_type"))
    local_path = clean_text(first_value(payload, ("local_path", "source_path", "path"), ""), 1500)
    url = clean_text(first_value(payload, ("client_safe_url", "public_url", "url", "preview_url", "asset_url"), ""), 1500)
    content_type = clean_text(payload.get("content_type") or content_type_for_path(local_path or url), 180)
    created_by_role = clean_text(payload.get("created_by_role") or payload.get("role") or "system", 80)
    client_visible = clean_bool(payload.get("client_visible"), default=True)

    reference = CanonicalAssetReference(
        asset_id=asset_id,
        customer_id=clean_text(first_value(payload, ("customer_id", "client_id"), ""), 180),
        account_id=clean_text(first_value(payload, ("account_id", "tenant_id"), ""), 180),
        tenant_id=clean_text(payload.get("tenant_id"), 180),
        job_id=clean_text(payload.get("job_id"), 180),
        asset_type=clean_text(payload.get("asset_type") or "asset", 120),
        media_type=clean_text(payload.get("media_type"), 120),
        source_type=source_type,
        local_path=local_path,
        storage_backend=clean_text(payload.get("storage_backend") or ("local_path" if local_path else "external_url"), 120),
        storage_key=clean_text(payload.get("storage_key") or payload.get("object_key") or asset_id, 1000),
        future_s3=build_future_s3_metadata(payload, source_type, asset_id),
        public_url=clean_text(payload.get("public_url"), 1500),
        client_safe_url=url,
        admin_url=clean_text(payload.get("admin_url") or url, 1500),
        content_type=content_type,
        size_bytes=clean_int(payload.get("size_bytes"), file_size_if_available(local_path)),
        checksum_sha256=clean_text(first_value(payload, ("checksum_sha256", "sha256", "hash"), ""), 180),
        created_at=clean_text(payload.get("created_at") or utc_now(), 80),
        created_by_role=created_by_role,
        client_visible=client_visible,
        admin_visible=clean_bool(payload.get("admin_visible"), default=True),
        retention={
            "retention_policy": clean_text(payload.get("retention_policy") or "standard", 120),
            "audit_hold": clean_bool(payload.get("audit_hold")),
            "delete_after": clean_text(payload.get("delete_after"), 120),
        },
        audit={
            "correlation_id": clean_text(payload.get("correlation_id"), 180),
            "request_id": clean_text(payload.get("request_id"), 180),
            "created_by_role": created_by_role,
            "asset_event_type": "asset_reference_prepared",
        },
        provider_source_metadata=redact_secret_values({
            "provider": clean_text(payload.get("provider"), 120),
            "provider_job_id": clean_text(payload.get("provider_job_id"), 180),
            "source_metadata": payload.get("source_metadata") if isinstance(payload.get("source_metadata"), dict) else {},
        }),
        diagnostics_visibility_rules={
            "admin_view_may_include_local_path": True,
            "client_view_hides_local_path": True,
            "client_view_hides_provider_diagnostics": True,
            "secret_values_always_redacted": True,
        },
        aws_s3_required=False,
        s3_upload_enabled=False,
    )
    return reference.to_dict()


def build_asset_reference_from_local_path(
    local_path: str,
    asset_type: str,
    **metadata: Any,
) -> Dict[str, Any]:
    return build_asset_reference({
        **metadata,
        "local_path": local_path,
        "asset_type": asset_type,
        "source_type": metadata.get("source_type") or "generated",
        "content_type": metadata.get("content_type") or content_type_for_path(local_path),
    })


def build_asset_reference_from_url(
    url: str,
    asset_type: str,
    **metadata: Any,
) -> Dict[str, Any]:
    return build_asset_reference({
        **metadata,
        "client_safe_url": url,
        "admin_url": metadata.get("admin_url") or url,
        "asset_type": asset_type,
        "source_type": metadata.get("source_type") or "provider_output",
        "storage_backend": metadata.get("storage_backend") or "external_url",
        "content_type": metadata.get("content_type") or content_type_for_path(url),
    })


def validate_asset_reference(reference: Mapping[str, Any] | None) -> Dict[str, Any]:
    reference = dict(reference or {})
    errors: List[str] = []
    for key in ("asset_id", "asset_type", "source_type", "created_at"):
        if not clean_text(reference.get(key)):
            errors.append(f"missing_{key}")
    if clean_text(reference.get("source_type")) not in SUPPORTED_SOURCE_TYPES:
        errors.append("unsupported_source_type")
    if has_unredacted_secret_value(reference):
        errors.append("possible_unredacted_secret_marker")

    return {
        "valid": not errors,
        "errors": errors,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_client_safe_asset_view(reference_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    reference = (
        dict(reference_or_payload or {})
        if "diagnostics_visibility_rules" in dict(reference_or_payload or {})
        else build_asset_reference(reference_or_payload)
    )
    return {
        "asset_id": reference.get("asset_id"),
        "job_id": reference.get("job_id"),
        "asset_type": reference.get("asset_type"),
        "media_type": reference.get("media_type"),
        "source_type": reference.get("source_type"),
        "client_safe_url": reference.get("client_safe_url") or reference.get("public_url"),
        "content_type": reference.get("content_type"),
        "size_bytes": reference.get("size_bytes"),
        "checksum_sha256": reference.get("checksum_sha256"),
        "created_at": reference.get("created_at"),
        "client_visible": bool(reference.get("client_visible")),
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "provider_secret_values_visible": False,
    }


def build_admin_safe_asset_view(reference_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    reference = (
        dict(reference_or_payload or {})
        if "diagnostics_visibility_rules" in dict(reference_or_payload or {})
        else build_asset_reference(reference_or_payload)
    )
    return redact_secret_values({
        "asset_id": reference.get("asset_id"),
        "customer_id": reference.get("customer_id"),
        "account_id": reference.get("account_id"),
        "tenant_id": reference.get("tenant_id"),
        "job_id": reference.get("job_id"),
        "asset_type": reference.get("asset_type"),
        "media_type": reference.get("media_type"),
        "source_type": reference.get("source_type"),
        "local_path": reference.get("local_path"),
        "storage_backend": reference.get("storage_backend"),
        "storage_key": reference.get("storage_key"),
        "future_s3": reference.get("future_s3") or {},
        "client_safe_url": reference.get("client_safe_url"),
        "admin_url": reference.get("admin_url"),
        "content_type": reference.get("content_type"),
        "size_bytes": reference.get("size_bytes"),
        "checksum_sha256": reference.get("checksum_sha256"),
        "created_at": reference.get("created_at"),
        "created_by_role": reference.get("created_by_role"),
        "client_visible": reference.get("client_visible"),
        "admin_visible": reference.get("admin_visible"),
        "retention": reference.get("retention") or {},
        "audit": reference.get("audit") or {},
        "provider_source_metadata": reference.get("provider_source_metadata") or {},
        "diagnostics_visibility_rules": reference.get("diagnostics_visibility_rules") or {},
        "customer_safe": True,
        "credential_values_exposed": False,
        "provider_secret_values_visible": False,
    })


class LocalNoopAssetStorageAdapter:
    """
    Safe AWS-04 asset storage boundary adapter.

    It prepares canonical asset references and reports local/no-op persistence
    while AWS_OPTION_A_ENABLED is false. It does not upload to S3, call providers,
    move local files, rewrite portal upload/output behavior, reserve credits, or
    change auth/session behavior.
    """

    def __init__(self, env: Optional[Mapping[str, Any]] = None):
        self.env = dict(env or {})
        self.readiness = aws_option_a_readiness(self.env)

    def persist_reference(self, reference_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
        reference = (
            dict(reference_or_payload or {})
            if "diagnostics_visibility_rules" in dict(reference_or_payload or {})
            else build_asset_reference(reference_or_payload)
        )
        validation = validate_asset_reference(reference)
        if not validation.get("valid"):
            return {
                "success": False,
                "accepted": False,
                "status": "asset_reference_invalid",
                "errors": validation.get("errors") or [],
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        if not self.readiness.get("aws_option_a_enabled"):
            return {
                "success": True,
                "accepted": True,
                "status": "local_noop_asset_reference_persisted",
                "storage_backend": "local_noop",
                "asset_id": reference.get("asset_id"),
                "reference": reference,
                "s3_upload_attempted": False,
                "paid_provider_calls_started": False,
                "portal_upload_behavior_changed": False,
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        return {
            "success": False,
            "accepted": False,
            "status": "aws_s3_adapter_not_enabled_yet",
            "storage_backend": "aws_s3_future_adapter",
            "asset_id": reference.get("asset_id"),
            "s3_upload_attempted": False,
            "paid_provider_calls_started": False,
            "customer_safe": True,
            "credential_values_exposed": False,
        }


def persist_asset_reference_locally_or_noop(
    reference_or_payload: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    return LocalNoopAssetStorageAdapter(env=env).persist_reference(reference_or_payload)
