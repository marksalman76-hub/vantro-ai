from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional
import mimetypes
import re
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
    "credentials_required_now",
    "credential_values_exposed",
    "provider_secret_values_visible",
    "requires_aws_credentials_now",
    "s3_upload_attempted",
    "aws_calls_started",
}

SUPPORTED_S3_DELIVERY_SOURCE_TYPES = {
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

DEFAULT_RETENTION_POLICY = {
    "policy": "future_customer_asset_retention_policy",
    "delete_after_days": None,
    "legal_hold_supported": True,
    "customer_export_supported": True,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "s3_asset") -> str:
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


def content_type_for_name(name: str, fallback: str = "application/octet-stream") -> str:
    return mimetypes.guess_type(name)[0] or fallback


def file_size_if_available(path: str) -> int:
    try:
        candidate = Path(path)
        if candidate.exists() and candidate.is_file():
            return candidate.stat().st_size
    except Exception:
        pass
    return 0


def normalise_source_type(value: Any) -> str:
    source_type = clean_text(value or "generated", 80).lower()
    return source_type if source_type in SUPPORTED_S3_DELIVERY_SOURCE_TYPES else "generated"


def sanitise_s3_segment(value: Any, fallback: str = "asset") -> str:
    text = clean_text(value, 180).replace("\\", "/").split("/")[-1]
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip(".-_").lower()
    return text or fallback


def filename_from_payload(payload: Mapping[str, Any], asset_id: str) -> str:
    explicit = clean_text(first_value(payload, ("filename", "file_name", "name"), ""), 240)
    if explicit:
        return sanitise_s3_segment(explicit, f"{asset_id}.bin")
    local_path = clean_text(first_value(payload, ("local_path", "source_path", "path"), ""), 1500)
    if local_path:
        return sanitise_s3_segment(Path(local_path).name, f"{asset_id}.bin")
    provider_url = clean_text(first_value(payload, ("provider_url", "url", "asset_url", "client_safe_url", "public_url"), ""), 1500)
    if provider_url:
        return sanitise_s3_segment(provider_url.rstrip("/").split("/")[-1], f"{asset_id}.bin")
    return f"{sanitise_s3_segment(asset_id, 'asset')}.bin"


def build_s3_key_strategy(payload: Mapping[str, Any], asset_id: str, filename: str) -> Dict[str, Any]:
    source_type = normalise_source_type(payload.get("source_type"))
    customer_ref = clean_text(first_value(payload, ("customer_id", "client_id", "account_id", "tenant_id"), "unassigned"), 120)
    job_ref = clean_text(payload.get("job_id") or "unassigned", 120)
    asset_type = sanitise_s3_segment(payload.get("asset_type") or source_type, "asset")
    checksum = clean_text(first_value(payload, ("checksum_sha256", "checksum", "hash"), ""), 128)
    suffix = checksum[:12] if checksum else f"{asset_id[-8:]}-pending-hash"
    return {
        "customer_namespace": f"customers/{sanitise_s3_segment(customer_ref, 'unassigned')}",
        "job_namespace": f"jobs/{sanitise_s3_segment(job_ref, 'unassigned')}",
        "asset_type_folder": asset_type,
        "source_type_folder": sanitise_s3_segment(source_type, "generated"),
        "sanitized_filename": sanitise_s3_segment(filename, f"{asset_id}.bin"),
        "collision_safe_suffix": suffix,
        "local_absolute_path_leaked_to_client": False,
        "key_version": "aws09-boundary-v1",
    }


def build_s3_key(strategy: Mapping[str, Any], asset_id: str) -> str:
    return "/".join(
        [
            clean_text(strategy.get("customer_namespace"), 240),
            clean_text(strategy.get("job_namespace"), 240),
            "assets",
            clean_text(strategy.get("asset_type_folder"), 120),
            clean_text(strategy.get("source_type_folder"), 120),
            sanitise_s3_segment(asset_id, "asset"),
            f"{strategy.get('collision_safe_suffix')}-{strategy.get('sanitized_filename')}",
        ]
    )


def choose_bucket(payload: Mapping[str, Any], readiness: Mapping[str, Any], source_type: str) -> str:
    explicit = clean_text(first_value(payload, ("s3_bucket", "bucket", "future_s3_bucket"), ""), 240)
    if explicit:
        return explicit
    if source_type == "upload":
        return clean_text(readiness.get("uploads_s3_bucket"), 240)
    return clean_text(readiness.get("media_s3_bucket"), 240)


@dataclass(frozen=True)
class CanonicalS3ObjectReference:
    asset_id: str
    job_id: str = ""
    customer_id: str = ""
    account_id: str = ""
    tenant_id: str = ""
    asset_type: str = "asset"
    source_type: str = "generated"
    content_type: str = "application/octet-stream"
    size_bytes: int = 0
    checksum_sha256: str = ""
    s3_bucket: str = ""
    s3_key: str = ""
    aws_region: str = ""
    storage_class: str = "STANDARD"
    client_safe_url: str = ""
    admin_url: str = ""
    support_url: str = ""
    signed_url_required: bool = True
    public_access_allowed: bool = False
    retention_policy: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_RETENTION_POLICY))
    created_at: str = field(default_factory=utc_now)
    local_path: str = ""
    provider_url: str = ""
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    key_strategy: Dict[str, Any] = field(default_factory=dict)
    s3_upload_attempted: bool = False
    aws_calls_started: bool = False
    credentials_required_now: bool = False
    customer_safe: bool = True
    credential_values_exposed: bool = False
    internal_config_exposed_to_client: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return redact_secret_values(asdict(self))


def build_s3_object_reference(
    payload: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    payload = dict(payload or {})
    readiness = aws_option_a_readiness(env or {})
    asset_id = clean_text(payload.get("asset_id") or safe_id("s3_asset"), 180)
    source_type = normalise_source_type(payload.get("source_type"))
    local_path = clean_text(first_value(payload, ("local_path", "source_path", "path"), ""), 1500)
    provider_url = clean_text(first_value(payload, ("provider_url", "url", "asset_url", "public_url"), ""), 1500)
    filename = filename_from_payload(payload, asset_id)
    content_type = clean_text(payload.get("content_type") or content_type_for_name(filename), 180)
    strategy = build_s3_key_strategy({**payload, "source_type": source_type}, asset_id, filename)
    bucket = choose_bucket(payload, readiness, source_type)
    key = clean_text(payload.get("s3_key") or payload.get("future_s3_key") or build_s3_key(strategy, asset_id), 1000)
    public_access_allowed = clean_bool(payload.get("public_access_allowed"), default=False)
    explicitly_safe_url = clean_text(first_value(payload, ("client_safe_url", "signed_url", "safe_url"), ""), 1500)

    reference = CanonicalS3ObjectReference(
        asset_id=asset_id,
        job_id=clean_text(payload.get("job_id"), 180),
        customer_id=clean_text(first_value(payload, ("customer_id", "client_id"), ""), 180),
        account_id=clean_text(first_value(payload, ("account_id", "tenant_id"), ""), 180),
        tenant_id=clean_text(payload.get("tenant_id"), 180),
        asset_type=clean_text(payload.get("asset_type") or "asset", 120),
        source_type=source_type,
        content_type=content_type,
        size_bytes=clean_int(payload.get("size_bytes"), file_size_if_available(local_path)),
        checksum_sha256=clean_text(first_value(payload, ("checksum_sha256", "checksum", "hash"), ""), 128),
        s3_bucket=bucket,
        s3_key=key,
        aws_region=clean_text(payload.get("aws_region") or readiness.get("aws_region"), 80),
        storage_class=clean_text(payload.get("storage_class") or "STANDARD", 80),
        client_safe_url=explicitly_safe_url,
        admin_url=clean_text(payload.get("admin_url") or (f"s3://{bucket}/{key}" if bucket and key else ""), 1500),
        support_url=clean_text(payload.get("support_url") or payload.get("correlation_id") or "", 500),
        signed_url_required=clean_bool(payload.get("signed_url_required"), default=not public_access_allowed),
        public_access_allowed=public_access_allowed,
        retention_policy=redact_secret_values(payload.get("retention_policy") or dict(DEFAULT_RETENTION_POLICY)),
        local_path=local_path,
        provider_url=provider_url,
        source_metadata=redact_secret_values(payload.get("source_metadata") or payload.get("provider_source_metadata") or {}),
        key_strategy=strategy,
        s3_upload_attempted=False,
        aws_calls_started=False,
        credentials_required_now=False,
    )
    return reference.to_dict()


def build_s3_object_reference_from_asset_reference(
    asset_reference: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    asset_reference = dict(asset_reference or {})
    future_s3 = dict(asset_reference.get("future_s3") or {})
    return build_s3_object_reference(
        {
            **asset_reference,
            "s3_bucket": future_s3.get("s3_bucket") or asset_reference.get("s3_bucket"),
            "s3_key": future_s3.get("s3_key") or asset_reference.get("s3_key"),
            "provider_url": asset_reference.get("provider_url") or asset_reference.get("public_url"),
            "source_metadata": asset_reference.get("provider_source_metadata") or asset_reference.get("source_metadata") or {},
        },
        env=env,
    )


def build_s3_object_reference_from_local_path(
    local_path: str,
    asset_type: str,
    env: Optional[Mapping[str, Any]] = None,
    **metadata: Any,
) -> Dict[str, Any]:
    return build_s3_object_reference(
        {
            **metadata,
            "local_path": local_path,
            "asset_type": asset_type,
            "source_type": metadata.get("source_type") or "generated",
            "content_type": metadata.get("content_type") or content_type_for_name(local_path),
        },
        env=env,
    )


def build_s3_object_reference_from_provider_url(
    provider_url: str,
    asset_type: str,
    env: Optional[Mapping[str, Any]] = None,
    **metadata: Any,
) -> Dict[str, Any]:
    return build_s3_object_reference(
        {
            **metadata,
            "provider_url": provider_url,
            "asset_type": asset_type,
            "source_type": metadata.get("source_type") or "provider_output",
            "content_type": metadata.get("content_type") or content_type_for_name(provider_url),
        },
        env=env,
    )


def validate_s3_object_reference(reference: Mapping[str, Any] | None) -> Dict[str, Any]:
    reference = dict(reference or {})
    errors: list[str] = []
    for key in ("asset_id", "asset_type", "source_type", "s3_key", "created_at"):
        if not clean_text(reference.get(key)):
            errors.append(f"missing_{key}")
    if clean_text(reference.get("source_type")) not in SUPPORTED_S3_DELIVERY_SOURCE_TYPES:
        errors.append("unsupported_source_type")
    if clean_bool(reference.get("public_access_allowed"), default=False):
        errors.append("public_access_must_be_explicitly_reviewed")
    if not isinstance(reference.get("signed_url_required"), bool):
        errors.append("signed_url_required_must_be_boolean")
    if has_unredacted_secret_value(reference):
        errors.append("possible_unredacted_secret_marker")
    return {
        "valid": not errors,
        "errors": errors,
        "s3_upload_attempted": False,
        "aws_calls_started": False,
        "credentials_required_now": False,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def build_client_safe_s3_delivery_view(reference_or_payload: Mapping[str, Any] | None) -> Dict[str, Any]:
    reference = (
        dict(reference_or_payload or {})
        if "key_strategy" in dict(reference_or_payload or {})
        else build_s3_object_reference(reference_or_payload)
    )
    return {
        "asset_id": reference.get("asset_id"),
        "job_id": reference.get("job_id"),
        "asset_type": reference.get("asset_type"),
        "source_type": reference.get("source_type"),
        "content_type": reference.get("content_type"),
        "size_bytes": reference.get("size_bytes"),
        "checksum_sha256": reference.get("checksum_sha256"),
        "client_safe_url": reference.get("client_safe_url"),
        "signed_url_required": bool(reference.get("signed_url_required", True)),
        "public_access_allowed": bool(reference.get("public_access_allowed", False)),
        "created_at": reference.get("created_at"),
        "customer_safe": True,
        "credential_values_exposed": False,
        "internal_config_exposed": False,
        "provider_secret_values_visible": False,
    }


def build_admin_safe_s3_readiness_view(
    reference_or_payload: Mapping[str, Any] | None,
    env: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    reference = (
        dict(reference_or_payload or {})
        if "key_strategy" in dict(reference_or_payload or {})
        else build_s3_object_reference(reference_or_payload, env=env)
    )
    readiness = aws_option_a_readiness(env or {})
    return redact_secret_values(
        {
            "asset_id": reference.get("asset_id"),
            "customer_id": reference.get("customer_id"),
            "account_id": reference.get("account_id"),
            "tenant_id": reference.get("tenant_id"),
            "job_id": reference.get("job_id"),
            "asset_type": reference.get("asset_type"),
            "source_type": reference.get("source_type"),
            "content_type": reference.get("content_type"),
            "size_bytes": reference.get("size_bytes"),
            "checksum_sha256": reference.get("checksum_sha256"),
            "s3_bucket": reference.get("s3_bucket"),
            "s3_key": reference.get("s3_key"),
            "aws_region": reference.get("aws_region"),
            "storage_class": reference.get("storage_class"),
            "signed_url_required": reference.get("signed_url_required"),
            "public_access_allowed": reference.get("public_access_allowed"),
            "retention_policy": reference.get("retention_policy") or {},
            "local_path": reference.get("local_path"),
            "provider_url": reference.get("provider_url"),
            "admin_url": reference.get("admin_url"),
            "support_url": reference.get("support_url"),
            "source_metadata": reference.get("source_metadata") or {},
            "key_strategy": reference.get("key_strategy") or {},
            "readiness": {
                "aws_option_a_enabled": readiness.get("aws_option_a_enabled"),
                "ready_for_aws_execution": readiness.get("ready_for_aws_execution"),
                "media_s3_bucket_configured": bool(readiness.get("media_s3_bucket")),
                "uploads_s3_bucket_configured": bool(readiness.get("uploads_s3_bucket")),
                "aws_region_configured": bool(readiness.get("aws_region")),
                "requires_aws_credentials_now": False,
                "s3_upload_attempted": False,
                "aws_calls_started": False,
            },
            "customer_safe": True,
            "credential_values_exposed": False,
            "provider_secret_values_visible": False,
        }
    )


def build_s3_delivery_boundary_readiness(env: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    readiness = aws_option_a_readiness(env or {})
    return {
        "boundary": "aws09_s3_asset_delivery_boundary",
        "aws_option_a_enabled": readiness.get("aws_option_a_enabled"),
        "ready_for_aws_execution": readiness.get("ready_for_aws_execution"),
        "supported_source_types": sorted(SUPPORTED_S3_DELIVERY_SOURCE_TYPES),
        "media_s3_bucket_configured": bool(readiness.get("media_s3_bucket")),
        "uploads_s3_bucket_configured": bool(readiness.get("uploads_s3_bucket")),
        "aws_region_configured": bool(readiness.get("aws_region")),
        "requires_aws_credentials_now": False,
        "credentials_required_now": False,
        "s3_upload_attempted": False,
        "aws_calls_started": False,
        "live_delivery_behavior_changed": False,
        "client_view_hides_bucket_key_and_local_path": True,
        "public_access_allowed_default": False,
        "signed_url_required_default": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
