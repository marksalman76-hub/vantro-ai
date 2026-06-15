from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping
import os


TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


def _enabled(value: Any) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def _clean(value: Any) -> str:
    return str(value or "").strip()


@dataclass(frozen=True)
class AwsOptionARuntimeContract:
    """
    Source-of-truth environment contract for AWS Option A migration.

    This module is intentionally non-invasive. It does not switch storage,
    queueing, provider execution, or portal behavior by itself. It lets the API,
    worker, tests, and deployment docs agree on the same AWS target variables
    while Render/Vercel-compatible local defaults keep working during migration.
    """

    aws_option_a_enabled: bool = False
    app_environment: str = "local"
    aws_region: str = ""
    backend_service_mode: str = "local_dev"
    media_worker_enabled: bool = False

    database_url_present: bool = False
    rds_secret_arn_present: bool = False
    media_s3_bucket: str = ""
    uploads_s3_bucket: str = ""
    media_queue_url_present: bool = False
    media_dlq_url_present: bool = False
    provider_secrets_prefix: str = ""
    cloudwatch_log_group: str = ""

    api_task_role_arn_present: bool = False
    worker_task_role_arn_present: bool = False
    admin_portal_authority_preserved: bool = True
    client_portal_safety_preserved: bool = True
    self_contained_create_media_popup_preserved: bool = True

    missing_required_for_aws: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ready_for_aws_execution(self) -> bool:
        return self.aws_option_a_enabled and not self.missing_required_for_aws

    def to_public_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["ready_for_aws_execution"] = self.ready_for_aws_execution
        data["credential_values_exposed"] = False
        data["provider_secret_values_visible"] = False
        data["customer_safe"] = True
        return data


def load_aws_option_a_runtime_contract(env: Mapping[str, Any] | None = None) -> AwsOptionARuntimeContract:
    env = env or os.environ
    enabled = _enabled(env.get("AWS_OPTION_A_ENABLED"))

    app_environment = _clean(env.get("APP_ENV") or env.get("ENVIRONMENT") or "local") or "local"
    aws_region = _clean(env.get("AWS_REGION") or env.get("AWS_DEFAULT_REGION"))
    backend_service_mode = _clean(env.get("AWS_BACKEND_SERVICE_MODE") or ("aws_option_a" if enabled else "local_dev"))
    media_worker_enabled = _enabled(env.get("AWS_MEDIA_WORKER_ENABLED")) or (
        enabled and _clean(env.get("SERVICE_ROLE")).lower() == "media_worker"
    )

    media_s3_bucket = _clean(env.get("AWS_MEDIA_S3_BUCKET") or env.get("MEDIA_S3_BUCKET"))
    uploads_s3_bucket = _clean(env.get("AWS_UPLOADS_S3_BUCKET") or env.get("UPLOADS_S3_BUCKET"))
    provider_secrets_prefix = _clean(env.get("AWS_PROVIDER_SECRETS_PREFIX") or env.get("PROVIDER_SECRETS_PREFIX"))
    cloudwatch_log_group = _clean(env.get("AWS_CLOUDWATCH_LOG_GROUP") or env.get("CLOUDWATCH_LOG_GROUP"))

    required_when_enabled = {
        "AWS_REGION": bool(aws_region),
        "DATABASE_URL or AWS_RDS_SECRET_ARN": bool(_clean(env.get("DATABASE_URL")) or _clean(env.get("AWS_RDS_SECRET_ARN"))),
        "AWS_MEDIA_S3_BUCKET": bool(media_s3_bucket),
        "AWS_MEDIA_QUEUE_URL": bool(_clean(env.get("AWS_MEDIA_QUEUE_URL"))),
        "AWS_MEDIA_DLQ_URL": bool(_clean(env.get("AWS_MEDIA_DLQ_URL"))),
        "AWS_PROVIDER_SECRETS_PREFIX": bool(provider_secrets_prefix),
    }
    missing = [name for name, present in required_when_enabled.items() if enabled and not present]

    warnings: list[str] = []
    if enabled and not media_worker_enabled:
        warnings.append("AWS_OPTION_A_ENABLED is true but AWS_MEDIA_WORKER_ENABLED/SERVICE_ROLE=media_worker is not active for this process.")
    if enabled and not cloudwatch_log_group:
        warnings.append("AWS_CLOUDWATCH_LOG_GROUP is not configured; CloudWatch logging should be added before production cutover.")
    if _clean(env.get("NEXT_PUBLIC_BACKEND_URL")) and enabled:
        warnings.append("Frontend may remain Vercel temporarily, but backend API should point at the AWS ALB/API endpoint before cutover.")

    return AwsOptionARuntimeContract(
        aws_option_a_enabled=enabled,
        app_environment=app_environment,
        aws_region=aws_region,
        backend_service_mode=backend_service_mode,
        media_worker_enabled=media_worker_enabled,
        database_url_present=bool(_clean(env.get("DATABASE_URL"))),
        rds_secret_arn_present=bool(_clean(env.get("AWS_RDS_SECRET_ARN"))),
        media_s3_bucket=media_s3_bucket,
        uploads_s3_bucket=uploads_s3_bucket,
        media_queue_url_present=bool(_clean(env.get("AWS_MEDIA_QUEUE_URL"))),
        media_dlq_url_present=bool(_clean(env.get("AWS_MEDIA_DLQ_URL"))),
        provider_secrets_prefix=provider_secrets_prefix,
        cloudwatch_log_group=cloudwatch_log_group,
        api_task_role_arn_present=bool(_clean(env.get("AWS_API_TASK_ROLE_ARN"))),
        worker_task_role_arn_present=bool(_clean(env.get("AWS_WORKER_TASK_ROLE_ARN"))),
        missing_required_for_aws=missing,
        warnings=warnings,
    )


def aws_option_a_readiness(env: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return load_aws_option_a_runtime_contract(env).to_public_dict()
