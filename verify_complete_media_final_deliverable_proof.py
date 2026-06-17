from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent

REQUIRED_TRUE_FIELDS = [
    "complete_media_final_deliverable_attempted",
    "owner_provider_approval_required",
    "provider_cost_cap_enforced",
    "long_form_generation_blocked_or_not_requested",
    "multi_agent_provider_fanout_blocked",
    "synthetic_non_customer_request",
    "durable_status_flow_passed",
    "provider_output_or_failure_recorded",
    "durable_asset_storage_passed",
    "client_safe_result_view_redacted",
    "admin_provider_diagnostics_redacted",
    "failure_path_supportable",
]

REQUIRED_FALSE_FIELDS = [
    "complete_media_final_deliverable_passed",
    "provider_call_attempted",
    "customer_asset_used",
    "customer_likeness_used",
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "stripe_live_charge_attempted",
    "customer_traffic_attempted",
    "public_cutover_enabled",
    "render_removal_attempted",
    "aws21_or_later_work_attempted",
]

FORBIDDEN_VALUES = [
    "STRIPE_SECRET_SHOULD_NOT_LEAK",
    "PROVIDER_SECRET_SHOULD_NOT_LEAK",
    "RUNWAY_SECRET_SHOULD_NOT_LEAK",
    "ELEVEN_SECRET_SHOULD_NOT_LEAK",
    "DATABASE_SECRET_SHOULD_NOT_LEAK",
    "QUEUE_SECRET_SHOULD_NOT_LEAK",
    "123456789012",
    "arn:aws:",
    "postgres://",
    "sk_live_",
    "sk_test_",
    "pk_live_",
    "424242424242",
    "https://sqs.",
    "X-Amz-Signature=SHOULD_NOT_LEAK",
]

FORBIDDEN_SOURCE_MARKERS = [
    "requests.",
    "httpx.",
    "stripe.",
    "boto3",
    ".connect(",
    ".execute(",
    ".send_message(",
    ".put_object(",
    "run_runway_text_to_video_quality_test(",
    "run_elevenlabs_tts_quality_test(",
    "run_kling_text_to_video_quality_test(",
    "execute_direct_media_provider_job(",
    "start_universal_complete_media_workflow(",
]

SIDE_EFFECT_KEYS = {
    "billing_mutation_attempted",
    "credit_mutation_attempted",
    "stripe_live_charge_attempted",
    "stripe_call_attempted",
    "customer_traffic_attempted",
    "public_cutover_enabled",
    "render_removal_attempted",
    "aws21_or_later_work_attempted",
    "media_generation_attempted",
    "customer_asset_used",
    "customer_likeness_used",
}


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


def assert_no_forbidden_values(value: object, label: str) -> None:
    text = str(value)
    for forbidden in FORBIDDEN_VALUES:
        require(forbidden not in text, f"{label} leaked forbidden value: {forbidden}")


def assert_no_side_effects(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in SIDE_EFFECT_KEYS:
                require(item is False, f"{label} attempted side effect: {key}")
            assert_no_side_effects(item, label)
    elif isinstance(value, list):
        for item in value:
            assert_no_side_effects(item, label)


class FakeBody:
    def __init__(self, body: bytes):
        self.body = body

    def read(self) -> bytes:
        return self.body


class FakeS3Client:
    def __init__(self):
        self.objects: dict[tuple[str, str], dict[str, Any]] = {}
        self.put_count = 0
        self.get_count = 0
        self.delete_count = 0

    def put_object(self, **kwargs: Any) -> dict:
        bucket = kwargs.get("Bucket")
        key = kwargs.get("Key")
        body = kwargs.get("Body") or b""
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.objects[(bucket, key)] = {
            "Body": body,
            "ContentType": kwargs.get("ContentType"),
            "Metadata": kwargs.get("Metadata") or {},
        }
        self.put_count += 1
        return {"ETag": "fake-etag"}

    def get_object(self, **kwargs: Any) -> dict:
        bucket = kwargs.get("Bucket")
        key = kwargs.get("Key")
        if (bucket, key) not in self.objects:
            raise KeyError("NoSuchKey")
        self.get_count += 1
        return {"Body": FakeBody(self.objects[(bucket, key)]["Body"])}

    def delete_object(self, **kwargs: Any) -> dict:
        bucket = kwargs.get("Bucket")
        key = kwargs.get("Key")
        self.objects.pop((bucket, key), None)
        self.delete_count += 1
        return {}

    def head_object(self, **kwargs: Any) -> dict:
        bucket = kwargs.get("Bucket")
        key = kwargs.get("Key")
        if (bucket, key) not in self.objects:
            raise KeyError("NoSuchKey")
        return {"ContentLength": len(self.objects[(bucket, key)]["Body"])}

    def generate_presigned_url(self, *_args: Any, **_kwargs: Any) -> str:
        return "https://signed.example.invalid/download?X-Amz-Signature=SHOULD_NOT_LEAK"


def fake_asset_env(asset_helper) -> dict[str, str]:
    return {
        asset_helper.AWS_SYNTHETIC_DURABLE_ASSET_PROOF_ENABLED_FLAG: "true",
        asset_helper.AWS_SYNTHETIC_DURABLE_ASSET_OWNER_APPROVED_FLAG: "true",
        asset_helper.AWS_SYNTHETIC_DURABLE_ASSET_VALIDATION_CONFIRMED_FLAG: "true",
        asset_helper.AWS_SYNTHETIC_DURABLE_ASSET_S3_WRITE_ENABLED_FLAG: "true",
        asset_helper.AWS_SYNTHETIC_DURABLE_ASSET_METADATA_READBACK_ENABLED_FLAG: "true",
        asset_helper.AWS_SYNTHETIC_DURABLE_ASSET_OPEN_DOWNLOAD_ENABLED_FLAG: "true",
        asset_helper.AWS_SYNTHETIC_DURABLE_ASSET_CLEANUP_ENABLED_FLAG: "true",
        "AWS_DURABLE_ASSET_S3_BUCKET": "synthetic-complete-media-proof-bucket",
    }


def main() -> int:
    proof_helper = load_module(
        "backend/app/runtime/complete_media_final_deliverable_proof.py",
        "complete_media_final_deliverable_proof_under_test",
    )
    asset_helper = load_module(
        "backend/app/runtime/aws_synthetic_durable_asset_delivery.py",
        "aws_synthetic_durable_asset_delivery_for_complete_media_proof",
    )

    proof_source = read("backend/app/runtime/complete_media_final_deliverable_proof.py")
    direct_media_source = read("backend/app/runtime/direct_media_provider_execution_runtime.py")
    master_plan = read("PRODUCTION_COMPLETION_MASTER_PLAN.md")
    audit_plan = read("PRODUCTION_FINISH_AUDIT_AND_GAP_PLAN.md")
    matrix = read("AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md")

    for marker in FORBIDDEN_SOURCE_MARKERS:
        require(marker not in proof_source, f"Complete media proof boundary must not contain live side-effect marker: {marker}")

    for marker in [
        "executor.submit(_run_audio_job)",
        "executor.submit(_run_visual_segment",
        "\"media_type\": \"audio\"",
        "\"media_type\": \"video\"",
    ]:
        require(marker in direct_media_source, f"Verifier expected current complete-media provider fanout marker: {marker}")

    require(
        "complete_media_final_deliverable_provider_call_limit" not in direct_media_source
        and "max_provider_call_count" not in direct_media_source,
        "If a dedicated provider-call cap was added, update this verifier to allow the live proof path.",
    )

    fake_s3 = FakeS3Client()
    asset_result = asset_helper.build_synthetic_durable_asset_delivery_proof(
        env=fake_asset_env(asset_helper),
        actor_role="admin",
        s3_client=fake_s3,
    )
    require(asset_result["durable_asset_proof_passed"] is True, "Injected fallback durable asset proof must pass.")
    require(fake_s3.put_count == 2, "Injected asset proof must store asset and metadata objects.")
    require(fake_s3.get_count == 2, "Injected asset proof must read asset and metadata objects.")
    require(fake_s3.delete_count == 2, "Injected asset proof must clean up asset and metadata objects.")

    proof = proof_helper.build_complete_media_final_deliverable_proof(
        asset_delivery_result=asset_result,
        allow_live_provider_attempt=False,
    )

    for field in REQUIRED_TRUE_FIELDS:
        require(proof.get(field) is True, f"Required proof field must be true: {field}")
    for field in REQUIRED_FALSE_FIELDS:
        require(proof.get(field) is False, f"Required proof field must be false: {field}")

    require(proof["provider_call_count"] == 0, "Blocked proof must not call providers.")
    require(
        proof["proof_blocked_reason"] == "blocked_no_one_provider_attempt_complete_media_path",
        "Proof must block because current complete-media path cannot satisfy the one-provider-attempt cap.",
    )
    require(
        proof["provider_attempt_shape"]["current_complete_media_provider_call_floor"] >= 2,
        "Current complete-media path must be recognized as visual plus audio provider calls.",
    )
    require(
        proof["provider_attempt_shape"]["one_provider_attempt_cap_satisfied"] is False,
        "Current complete-media path must not be treated as satisfying the one-provider cap.",
    )
    require(
        proof["cost_cap_decision"]["provider_execution_allowed_after_cost_gate"] is True,
        "Within-cap fixture should be allowed by the cost gate.",
    )
    require(
        proof["over_cap_block_decision"]["provider_cost_cap_blocked_without_approval"] is True,
        "Over-cap fixture must be blocked without owner approval.",
    )
    require(
        "two-provider-call 5s complete-media smoke" in proof["next_operator_action"],
        "Next operator action must name the explicit approval needed.",
    )

    client_view = proof["client_safe_result_view"]
    require(client_view["customer_safe"] is True, "Client view must be customer safe.")
    for hidden in ["failed_preflight_checks", "provider_attempt_shape", "cost_cap_decision", "over_cap_block_decision"]:
        require(hidden not in client_view, f"Client view must not expose internal diagnostic key: {hidden}")

    admin_diagnostics = proof["admin_provider_diagnostics"]
    require(admin_diagnostics["admin_provider_diagnostics_redacted"] is True, "Admin diagnostics must be redacted.")
    require(admin_diagnostics["credential_values_exposed"] is False, "Admin diagnostics must hide credentials.")
    require(admin_diagnostics["provider_secret_values_visible"] is False, "Admin diagnostics must hide provider secrets.")

    assert_no_side_effects(proof, "complete media final deliverable proof")
    assert_no_forbidden_values(proof, "complete media final deliverable proof")

    for marker in [
        "Complete media final deliverable proof",
        "complete_media_final_deliverable_attempted=true",
        "complete_media_final_deliverable_passed=false",
        "provider_call_attempted=false",
        "blocked_no_one_provider_attempt_complete_media_path",
    ]:
        require(
            marker in master_plan or marker in audit_plan or marker in matrix,
            f"Production docs missing complete-media proof marker: {marker}",
        )

    summary = {
        field: proof.get(field)
        for field in [*REQUIRED_TRUE_FIELDS, *REQUIRED_FALSE_FIELDS]
    }
    summary.update({
        "provider_call_count": proof.get("provider_call_count"),
        "proof_blocked_reason": proof.get("proof_blocked_reason"),
        "provider_selected_redacted_or_named_safe": proof.get("provider_selected_redacted_or_named_safe"),
        "synthetic_job_reference_hash": proof.get("synthetic_job_reference_hash"),
        "synthetic_tenant_reference_hash": proof.get("synthetic_tenant_reference_hash"),
    })
    print("COMPLETE_MEDIA_FINAL_DELIVERABLE_PROOF:")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("COMPLETE_MEDIA_FINAL_DELIVERABLE_VERIFICATION_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
