from __future__ import annotations

from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parent


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8", errors="ignore")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_contract_module():
    path = ROOT / "backend/app/runtime/aws_option_a_runtime_contract.py"
    spec = importlib.util.spec_from_file_location("aws_option_a_runtime_contract_under_test", path)
    if not spec or not spec.loader:
        raise AssertionError("Could not load AWS Option A runtime contract module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_contract_module()
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")
    env_example = read(".env.example")
    contract_source = read("backend/app/runtime/aws_option_a_runtime_contract.py")

    local = module.aws_option_a_readiness({})
    require(local["aws_option_a_enabled"] is False, "AWS Option A must be disabled by default.")
    require(local["ready_for_aws_execution"] is False, "Local/default mode must not claim AWS execution readiness.")
    require(local["missing_required_for_aws"] == [], "Disabled AWS mode must not block Render/Vercel-compatible local runs.")
    require(local["credential_values_exposed"] is False, "Readiness output must not expose credentials.")

    partial = module.aws_option_a_readiness({"AWS_OPTION_A_ENABLED": "true", "AWS_REGION": "ap-southeast-2"})
    require(partial["aws_option_a_enabled"] is True, "AWS Option A enabled flag must be recognized.")
    require(partial["ready_for_aws_execution"] is False, "Partial AWS config must not be ready.")
    for missing in [
        "DATABASE_URL or AWS_RDS_SECRET_ARN",
        "AWS_MEDIA_S3_BUCKET",
        "AWS_MEDIA_QUEUE_URL",
        "AWS_MEDIA_DLQ_URL",
        "AWS_PROVIDER_SECRETS_PREFIX",
    ]:
        require(missing in partial["missing_required_for_aws"], f"Missing required AWS env was not reported: {missing}")

    complete = module.aws_option_a_readiness({
        "AWS_OPTION_A_ENABLED": "true",
        "APP_ENV": "production",
        "AWS_REGION": "ap-southeast-2",
        "AWS_BACKEND_SERVICE_MODE": "aws_option_a",
        "AWS_MEDIA_WORKER_ENABLED": "true",
        "DATABASE_URL": "postgres://redacted",
        "AWS_MEDIA_S3_BUCKET": "media-bucket",
        "AWS_UPLOADS_S3_BUCKET": "uploads-bucket",
        "AWS_MEDIA_QUEUE_URL": "https://sqs.example/media",
        "AWS_MEDIA_DLQ_URL": "https://sqs.example/media-dlq",
        "AWS_PROVIDER_SECRETS_PREFIX": "/ecommerce-ai-agent-platform/providers/",
        "AWS_CLOUDWATCH_LOG_GROUP": "/ecs/ecommerce-ai-agent-platform/media",
        "AWS_API_TASK_ROLE_ARN": "arn:aws:iam::123:role/api",
        "AWS_WORKER_TASK_ROLE_ARN": "arn:aws:iam::123:role/worker",
    })
    require(complete["ready_for_aws_execution"] is True, "Complete AWS env contract must be ready.")
    require(complete["database_url_present"] is True, "Database URL presence must be detected without exposing its value.")
    require("postgres://redacted" not in str(complete), "Database URL value must not be exposed in public readiness.")
    require(complete["admin_portal_authority_preserved"] is True, "Admin authority preservation marker is missing.")
    require(complete["client_portal_safety_preserved"] is True, "Client safety preservation marker is missing.")
    require(complete["self_contained_create_media_popup_preserved"] is True, "Create Media popup preservation marker is missing.")

    for marker in [
        "AWS_OPTION_A_ENABLED",
        "AWS_MEDIA_S3_BUCKET",
        "AWS_MEDIA_QUEUE_URL",
        "AWS_MEDIA_DLQ_URL",
        "AWS_PROVIDER_SECRETS_PREFIX",
        "AWS_CLOUDWATCH_LOG_GROUP",
    ]:
        require(marker in env_example, f".env.example missing AWS contract marker: {marker}")
        require(marker in matrix, f"Migration matrix missing AWS contract marker: {marker}")

    for marker in [
        "AwsOptionARuntimeContract",
        "load_aws_option_a_runtime_contract",
        "aws_option_a_readiness",
        "ready_for_aws_execution",
        "credential_values_exposed",
    ]:
        require(marker in contract_source, f"AWS contract source missing marker: {marker}")

    for marker in [
        "AWS-01",
        "AWS-02",
        "AWS-03",
        "ECS/Fargate backend API service",
        "Separate ECS/Fargate media worker service with ffmpeg",
        "SQS media queue and dead-letter queue",
        "RDS PostgreSQL durable job/customer/asset/audit data",
        "S3 durable media/object storage",
        "Admin/client authority separation",
        "verify_aws_option_a_runtime_contract.py",
    ]:
        require(marker in matrix, f"Migration matrix missing implementation row marker: {marker}")

    print("AWS_OPTION_A_RUNTIME_CONTRACT_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
