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
    secrets = load_module(
        "backend/app/runtime/secrets_manager_config_boundary.py",
        "secrets_manager_config_boundary_under_test",
    )
    aws_contract = load_module(
        "backend/app/runtime/aws_option_a_runtime_contract.py",
        "aws_option_a_runtime_contract_for_secrets_test",
    )
    catalogue = load_module(
        "backend/app/runtime/real_agent_component_catalogue.py",
        "real_agent_component_catalogue_for_secrets_test",
    )

    source = read("backend/app/runtime/secrets_manager_config_boundary.py")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in [
        "import boto3",
        "from boto3",
        "get_secret_value(",
        "secretsmanager",
        "SecretId=",
        "requests.",
        "httpx.",
        "subprocess.",
    ]:
        require(marker not in source, f"AWS-10 boundary must not contain live secret/network marker: {marker}")

    env = {
        "AWS_OPTION_A_ENABLED": "true",
        "AWS_REGION": "ap-southeast-2",
        "AWS_PROVIDER_SECRETS_PREFIX": "/prod/ecommerce-ai-agent-platform",
        "RUNWAY_API_KEY": "RUNWAY_VALUE_MUST_NOT_LEAK",
        "ELEVENLABS_API_KEY": "ELEVENLABS_VALUE_MUST_NOT_LEAK",
        "OPENAI_API_KEY": "OPENAI_VALUE_MUST_NOT_LEAK",
        "STRIPE_SECRET_KEY": "STRIPE_VALUE_MUST_NOT_LEAK",
        "STRIPE_WEBHOOK_SECRET": "STRIPE_WEBHOOK_VALUE_MUST_NOT_LEAK",
        "DATABASE_URL": "postgres://USER:PASSWORD_VALUE_MUST_NOT_LEAK@example/db",
        "AWS_MEDIA_S3_BUCKET": "future-media-bucket",
        "AWS_UPLOADS_S3_BUCKET": "future-upload-bucket",
        "AWS_MEDIA_QUEUE_URL": "https://sqs.example/media",
        "AWS_MEDIA_DLQ_URL": "https://sqs.example/media-dlq",
        "JWT_SECRET": "JWT_VALUE_MUST_NOT_LEAK",
        "ADMIN_PLATFORM_TOKEN": "ADMIN_TOKEN_VALUE_MUST_NOT_LEAK",
        "CLIENT_PORTAL_SESSION_SECRET": "CLIENT_SESSION_VALUE_MUST_NOT_LEAK",
        "WEBHOOK_SIGNING_SECRET": "WEBHOOK_VALUE_MUST_NOT_LEAK",
        "SENTRY_DSN": "SENTRY_VALUE_MUST_NOT_LEAK",
    }
    env_before = dict(env)
    inventory = secrets.build_secret_inventory(env)
    admin_view = secrets.build_admin_safe_secret_readiness_view(env)
    client_view = secrets.build_client_safe_secret_readiness_view(env)
    readiness = secrets.build_secrets_manager_boundary_readiness(env)
    validation = secrets.validate_secret_inventory_no_values(inventory)
    aws_readiness_before = aws_contract.aws_option_a_readiness(env_before)
    aws_readiness_after = aws_contract.aws_option_a_readiness(env)

    require(env == env_before, "Secrets boundary must not mutate current environment mapping.")
    require(aws_readiness_before == aws_readiness_after, "Secrets boundary must not change current AWS env behavior.")
    require(validation["valid"] is True, f"Secret inventory should validate without values: {validation}")
    require(readiness["valid"] is True, "Secrets boundary readiness should be valid.")
    require(readiness["aws_fetch_attempted"] is False, "Secrets boundary must not fetch from AWS.")
    require(readiness["secrets_manager_call_attempted"] is False, "Secrets boundary must not call Secrets Manager.")
    require(readiness["credentials_required_now"] is False, "Secrets boundary must not require AWS credentials.")
    require(readiness["provider_execution_changed"] is False, "Secrets boundary must not change provider execution.")
    require(readiness["stripe_behavior_changed"] is False, "Secrets boundary must not change Stripe behavior.")
    require(readiness["auth_session_behavior_changed"] is False, "Secrets boundary must not change auth/session behavior.")
    require(readiness["frontend_behavior_changed"] is False, "Secrets boundary must not change frontend behavior.")

    expected_categories = {
        "media_providers",
        "llm_api_providers",
        "stripe_billing",
        "rds_database",
        "s3_storage",
        "sqs_queue",
        "auth_session_admin_tokens",
        "client_portal_session",
        "integrations_webhooks",
        "observability",
    }
    require(expected_categories.issubset(set(inventory["categories"])), "AWS-10 must cover the full paid SaaS secret/config surface.")
    require(inventory["total_secret_reference_count"] >= 15, "AWS-10 inventory should include broad platform secret/config references.")

    serialized_inventory = str(inventory)
    serialized_admin = str(admin_view)
    serialized_client = str(client_view)
    for forbidden_value in [
        "RUNWAY_VALUE_MUST_NOT_LEAK",
        "ELEVENLABS_VALUE_MUST_NOT_LEAK",
        "OPENAI_VALUE_MUST_NOT_LEAK",
        "STRIPE_VALUE_MUST_NOT_LEAK",
        "STRIPE_WEBHOOK_VALUE_MUST_NOT_LEAK",
        "PASSWORD_VALUE_MUST_NOT_LEAK",
        "JWT_VALUE_MUST_NOT_LEAK",
        "ADMIN_TOKEN_VALUE_MUST_NOT_LEAK",
        "CLIENT_SESSION_VALUE_MUST_NOT_LEAK",
        "WEBHOOK_VALUE_MUST_NOT_LEAK",
        "SENTRY_VALUE_MUST_NOT_LEAK",
    ]:
        require(forbidden_value not in serialized_inventory, f"Inventory leaked raw secret value: {forbidden_value}")
        require(forbidden_value not in serialized_admin, f"Admin view leaked raw secret value: {forbidden_value}")
        require(forbidden_value not in serialized_client, f"Client view leaked raw secret value: {forbidden_value}")

    for ref in inventory["secret_references"]:
        require("value_present" in ref, "Each secret reference must include value_present boolean.")
        require(isinstance(ref["value_present"], bool), "value_present must be boolean only.")
        require("value" not in ref, "Secret reference must not serialize a raw value key.")
        require("current_value" not in ref, "Secret reference must not serialize current_value.")
        require("secret_value" not in ref, "Secret reference must not serialize secret_value.")
        require(ref["aws_fetch_attempted"] is False, "Secret reference must not fetch AWS.")
        require(ref["secrets_manager_call_attempted"] is False, "Secret reference must not call Secrets Manager.")
        require(ref["credentials_required_now"] is False, "Secret reference must not require credentials now.")
        require(ref["future_secrets_manager_name"].startswith("/"), "Future Secrets Manager name placeholder must be path-like.")
        require(ref["status"] in {"env_placeholder_present", "missing", "not_configured"}, "Unexpected secret readiness status.")

    runway_ref = next(ref for ref in inventory["secret_references"] if ref["logical_name"] == "runway_provider_key")
    require(runway_ref["current_env_name"] == "RUNWAY_API_KEY", "Admin inventory must preserve current env name for Runway.")
    require(runway_ref["value_present"] is True, "Runway key presence must be represented as boolean true.")
    require(runway_ref["status"] == "env_placeholder_present", "Present env placeholder should report env_placeholder_present.")

    missing_inventory = secrets.build_secret_inventory({})
    missing_runway = next(ref for ref in missing_inventory["secret_references"] if ref["logical_name"] == "runway_provider_key")
    optional_kling = next(ref for ref in missing_inventory["secret_references"] if ref["logical_name"] == "kling_provider_key")
    require(missing_runway["value_present"] is False, "Missing secret presence must be boolean false.")
    require(missing_runway["status"] == "missing", "Required missing secret should report missing.")
    require(optional_kling["status"] == "not_configured", "Optional missing secret should report not_configured.")

    for hidden in [
        "RUNWAY_API_KEY",
        "STRIPE_SECRET_KEY",
        "DATABASE_URL",
        "AWS_MEDIA_QUEUE_URL",
        "JWT_SECRET",
        "ADMIN_PLATFORM_TOKEN",
        "future_secrets_manager_name",
        "secret_references",
        "missing_required_logical_names",
    ]:
        require(hidden not in serialized_client, f"Client-safe view must hide secret/internal name: {hidden}")
    require(client_view["credential_values_exposed"] is False, "Client view must not expose credential values.")
    require(client_view["internal_config_exposed"] is False, "Client view must not expose internal config.")

    require("RUNWAY_API_KEY" in serialized_admin, "Admin-safe view may include env names for readiness.")
    require("future_secrets_manager_name" in serialized_admin, "Admin-safe view must include future Secrets Manager placeholders.")
    require(admin_view["credential_values_exposed"] is False, "Admin view must not expose credential values.")
    require(admin_view["provider_secret_values_visible"] is False, "Admin view must not expose provider secret values.")

    visible = catalogue.list_final_approved_visible_agents()
    enterprise_selectable = catalogue.list_client_selectable_agents("enterprise")
    system_keys = {agent["key"] for agent in catalogue.SYSTEM_AGENTS}
    selectable_keys = {agent["key"] for agent in enterprise_selectable["agents"]}
    require(visible["count"] == 27, "AWS-10 must not alter final 27 visible catalogue count.")
    require(enterprise_selectable["count"] == 27, "AWS-10 must not alter enterprise selectable count.")
    require(not system_keys.intersection(selectable_keys), "AWS-10 must not expose SYSTEM_AGENTS as client-selectable.")

    for marker in [
        "AWS-10",
        "Secrets Manager config boundary",
        "verify_secrets_manager_config_boundary.py",
        "no AWS/Secrets Manager call",
        "full paid SaaS secret/config surface",
        "value_present booleans only",
    ]:
        require(marker in matrix, f"Migration matrix missing AWS-10 marker: {marker}")

    print("SECRETS_MANAGER_CONFIG_BOUNDARY_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
