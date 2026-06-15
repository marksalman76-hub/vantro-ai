from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import re
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


def load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AssertionError(f"Could not load module: {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    validator = load_module(
        "live_validate_aws_option_a_environment.py",
        "live_validate_aws_option_a_environment_under_test",
    )
    source = read("live_validate_aws_option_a_environment.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    default_result = validator.run_validation({})
    require(default_result["status"] == "skipped_live_validation_not_enabled", "Default validation must be skipped/blocked.")
    require(default_result["live_validation_enabled"] is False, "Default validation must not be live.")
    require(default_result["network_call_attempted"] is False, "Default validation must not attempt network.")
    require(default_result["credentials_required"] is False, "Default validation must not require credentials.")
    require(default_result["secrets_exposed"] is False, "Default validation must not expose secrets.")

    service_flag_without_live = validator.run_validation({"AWS_OPTION_A_VALIDATE_IAM": "true"})
    require(service_flag_without_live["status"] == "skipped_live_validation_not_enabled", "Service flags alone must not run live validation.")

    class NoCredentialsError(Exception):
        pass

    class FakeStsClient:
        def get_caller_identity(self):
            raise NoCredentialsError("Unable to locate credentials")

    class FakeSession:
        def __init__(self, *args, **kwargs):
            pass

        def client(self, service_name):
            require(service_name == "sts", "Missing-credential verifier must only exercise STS.")
            return FakeStsClient()

    class FakeBoto3:
        Session = FakeSession

    original_optional_dependency = validator.optional_dependency

    def fake_optional_dependency(module_name: str):
        if module_name == "boto3":
            return FakeBoto3
        return original_optional_dependency(module_name)

    validator.optional_dependency = fake_optional_dependency
    try:
        missing_credentials_result = validator.run_validation({
            "AWS_OPTION_A_LIVE_VALIDATION": "true",
            "AWS_OPTION_A_VALIDATE_IAM": "true",
        })
    finally:
        validator.optional_dependency = original_optional_dependency

    iam_missing_credentials = missing_credentials_result["service_results"]["iam"]
    missing_credentials_json = json.dumps(missing_credentials_result, sort_keys=True, default=str)
    require(
        iam_missing_credentials["status"] == "blocked_missing_aws_credentials",
        "Missing AWS credentials must return blocked_missing_aws_credentials.",
    )
    require("Traceback" not in missing_credentials_json, "Missing credentials must not produce a traceback.")
    require("AKIA" not in missing_credentials_json and "ASIA" not in missing_credentials_json, "Validation output must not expose access keys.")
    require("secret access key" not in missing_credentials_json.lower(), "Validation output must not expose secret keys.")

    for marker in [
        "AWS_OPTION_A_LIVE_VALIDATION",
        "AWS_OPTION_A_VALIDATE_RDS",
        "AWS_OPTION_A_VALIDATE_SQS",
        "AWS_OPTION_A_VALIDATE_S3",
        "AWS_OPTION_A_VALIDATE_SECRETS",
        "AWS_OPTION_A_VALIDATE_IAM",
        "AWS_OPTION_A_VALIDATE_SQS_TEST_MESSAGE",
        "AWS_OPTION_A_VALIDATE_S3_TEST_OBJECT",
        "AWS_OPTION_A_VALIDATE_SECRET_VALUE",
    ]:
        require(marker in source, f"Validation script missing live gate marker: {marker}")

    require("live_service_requested(env, \"iam\")" in source, "IAM validation must be live-gated.")
    require("live_service_requested(env, \"rds\")" in source, "RDS validation must be live-gated.")
    require("live_service_requested(env, \"sqs\")" in source, "SQS validation must be live-gated.")
    require("live_service_requested(env, \"s3\")" in source, "S3 validation must be live-gated.")
    require("live_service_requested(env, \"secrets\")" in source, "Secrets validation must be live-gated.")

    sqs_flag_index = source.index("AWS_OPTION_A_VALIDATE_SQS_TEST_MESSAGE")
    send_index = source.index("send_message(")
    delete_message_index = source.index("delete_message(")
    require(sqs_flag_index < send_index, "SQS test message send must be gated by explicit test-message flag.")
    require(send_index < delete_message_index, "SQS test message must have delete cleanup path.")
    require("cleanup_performed" in source, "SQS/S3 live validation must report cleanup.")

    s3_flag_index = source.index("AWS_OPTION_A_VALIDATE_S3_TEST_OBJECT")
    put_index = source.index("put_object(")
    delete_object_index = source.index("delete_object(")
    require(s3_flag_index < put_index, "S3 test object upload must be gated by explicit test-object flag.")
    require(put_index < delete_object_index, "S3 test object must have delete cleanup path.")

    secret_value_flag_index = source.index("AWS_OPTION_A_VALIDATE_SECRET_VALUE")
    get_secret_index = source.index("get_secret_value(")
    require(secret_value_flag_index < get_secret_index, "Secret value retrieval must be gated by explicit secret-value flag.")
    require("\"value_printed\": False" in source, "Secret validation must never print secret values.")
    require("\"secret_value_printed\": False" in source, "Top-level validation must report secret values are not printed.")
    require("sha256_12" in source and "length" in source, "Secret value live validation must expose only hash/length metadata.")

    forbidden_migration_or_cutover_markers = [
        "CREATE TABLE",
        "ALTER TABLE",
        "DROP TABLE",
        "INSERT INTO",
        "UPDATE ",
        "production_migration_attempted\": True",
        "route_cutover_attempted\": True",
        "provider_calls_attempted\": True",
        "stripe_mutation_attempted\": True",
        "credit_mutation_attempted\": True",
    ]
    for marker in forbidden_migration_or_cutover_markers:
        require(marker not in source, f"Validation script must not contain production mutation/cutover marker: {marker}")
    require("cur.execute(\"SELECT 1\")" in source, "RDS validation must be read-only SELECT 1.")

    for marker in [
        "blocked_missing_dependency_boto3",
        "blocked_missing_dependency_psycopg",
        "blocked_missing_aws_credentials",
        "blocked_aws_config_error",
        "aws_client_error",
        "botocore.exceptions",
        "safe_error_message",
        "apply_safe_aws_exception",
        "optional_dependency",
    ]:
        require(marker in source, f"Validation script must report missing optional dependencies safely: {marker}")

    row_ids = [int(match) for match in re.findall(r"AWS-(\d+)", matrix)]
    require(row_ids, "Migration matrix must contain AWS rows.")
    require(max(row_ids) <= 20, "Migration matrix must not expand beyond AWS-20.")
    require("AWS-21" not in matrix, "Migration matrix must not contain AWS-21 or later.")
    for marker in [
        "AWS-15",
        "AWS-15A",
        "controlled AWS environment validation",
        "live_validate_aws_option_a_environment.py",
        "verify_live_aws_option_a_environment_validation.py",
        "default no-live/no-network",
        "service-specific live validation flags",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-15A marker: {marker}")

    print("LIVE_AWS_OPTION_A_ENVIRONMENT_VALIDATION_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
