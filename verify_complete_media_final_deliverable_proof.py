from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent

REQUIRED_TRUE_FIELDS = [
    "full_media_stack_mapping_attempted",
    "full_media_stack_mapping_passed",
    "complete_media_final_deliverable_attempted",
    "owner_provider_approval_required",
    "provider_cost_cap_enforced",
    "provider_environment_readiness_attempted",
    "provider_category_readiness_attempted",
    "provider_router_used",
    "caption_or_subtitle_path_ready_or_not_required",
    "fallback_safe_artifact_path_ready",
    "duration_seconds_lte_5",
    "single_agent_mode_enforced",
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
    "provider_pair_hardcoded",
    "dotenv_values_exposed",
    "env_values_exposed",
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
    "visual_intermediate_asset_recorded",
    "audio_intermediate_asset_recorded",
    "composition_attempted",
    "composition_provider_call_attempted",
    "final_combined_asset_created",
    "final_combined_asset_playable_or_openable",
    "final_deliverable_is_single_combined_file",
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
        "executable_visual_providers",
        "executable_audio_providers",
        "two_provider_smoke_test",
        "max_visual_provider_calls",
        "max_audio_provider_calls",
        "max_total_provider_calls",
        "max_provider_retries",
        "executable_visual_provider_order = executable_visual_provider_order[:max_visual_provider_calls]",
        "visual_provider_call_count",
        "audio_provider_call_count",
        "provider_retry_count",
    ]:
        require(marker in direct_media_source, f"Verifier expected current complete-media provider fanout marker: {marker}")

    for marker in [
        "build_provider_category_readiness_snapshot",
        "provider_router_used",
        "provider_pair_hardcoded",
        "provider_category_readiness_not_verified",
        "selected_visual_provider_safe_name",
        "selected_audio_provider_safe_name",
        "selected_composition_method_safe_name",
        "complete_media_executable_provider_matrix_redacted",
        "required_env_names_by_provider",
        "dotenv_local_loaded",
        "dotenv_values_exposed",
        "env_values_exposed",
        "provider_environment_readiness_attempted",
        "provider_environment_readiness_passed",
        "caption_or_subtitle_path_ready_or_not_required",
        "fallback_safe_artifact_path_ready",
        "discovered_visual_provider_safe_names",
        "discovered_audio_provider_safe_names",
        "discovered_composition_safe_names",
        "discovered_caption_safe_names",
        "discovered_fallback_safe_names",
        "provider_category_readiness_attempted",
        "visual_provider_category_ready",
        "audio_provider_category_ready",
        "composition_method_ready",
        "duration_seconds_lte_5",
        "single_agent_mode_enforced",
    ]:
        require(marker in proof_source, f"Complete media proof must expose router/category proof marker: {marker}")

    for forbidden in [
        "Load/verify Runway and ElevenLabs credentials",
        "runway_credential_readiness_verified",
        "elevenlabs_credential_readiness_verified",
        "both_provider_readiness_verified",
        '"video_provider": "runway"',
        '"audio_provider": "elevenlabs"',
    ]:
        require(forbidden not in proof_source, f"Complete media proof must not hardcode provider-pair readiness: {forbidden}")

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
    require(proof["visual_provider_call_count"] == 0, "Safe-default proof must not call a visual provider.")
    require(proof["audio_provider_call_count"] == 0, "Safe-default proof must not call an audio provider.")
    require(proof["provider_retry_count"] == 0, "Safe-default proof must not retry providers.")
    require(proof["provider_router_used"] is True, "Complete-media proof must use the provider router.")
    require(proof["provider_pair_hardcoded"] is False, "Complete-media proof must not hardcode one provider pair.")
    require(proof["dotenv_values_exposed"] is False, "Local dotenv values must not be exposed.")
    require(proof["env_values_exposed"] is False, "Environment values must not be exposed.")
    require(proof["provider_category_readiness_attempted"] is True, "Provider category readiness must be attempted.")
    require(proof["provider_environment_readiness_attempted"] is True, "Provider environment readiness must be attempted.")
    require(proof["duration_seconds_lte_5"] is True, "Complete-media proof must stay at 5 seconds or less.")
    require(proof["single_agent_mode_enforced"] is True, "Complete-media proof must enforce single-agent mode.")
    require(
        proof["proof_blocked_reason"] in {
            "provider_category_readiness_not_verified",
            "blocked_live_provider_execution_not_requested",
            "blocked_preflight_not_ready",
        },
        "Safe-default proof must block before live provider execution with a router/category-safe reason.",
    )
    require(
        proof["provider_attempt_shape"]["current_complete_media_provider_call_floor"] >= 2,
        "Current complete-media path must be recognized as visual plus audio provider calls.",
    )
    require(
        proof["provider_attempt_shape"]["two_provider_attempt_cap_satisfied"] is True,
        "Current complete-media path must be treated as satisfying the approved two-provider cap.",
    )
    require(
        proof["provider_attempt_shape"]["provider_router_used"] is True,
        "Current complete-media path must be recognized as router-selected.",
    )
    require(
        proof["provider_attempt_shape"]["provider_pair_hardcoded"] is False,
        "Current complete-media path must not be marked as provider-pair hardcoded.",
    )
    category_readiness = proof.get("provider_category_readiness") or {}
    categories = category_readiness.get("categories") or {}
    require(category_readiness.get("provider_category_readiness_attempted") is True, "Category readiness snapshot must be marked attempted.")
    require(
        proof["visual_provider_category_ready"] == proof["visual_provider_readiness_verified"],
        "Visual category alias must match visual readiness.",
    )
    require(
        proof["audio_provider_category_ready"] == proof["audio_provider_readiness_verified"],
        "Audio category alias must match audio readiness.",
    )
    for category in [
        "visual_video_image",
        "voice_audio_music_sfx",
        "composition_stitching_internal",
        "caption_subtitle_paths",
        "fallback_safe_artifact_paths",
        "future_registered_provider_stack",
    ]:
        require(category in categories, f"Provider category readiness missing: {category}")
        require(categories[category].get("credential_values_exposed") is False, f"Category leaked credentials: {category}")
        require(categories[category].get("customer_safe") is True, f"Category must be customer safe: {category}")
    visual_names = set(categories["visual_video_image"].get("provider_safe_names") or [])
    audio_names = set(categories["voice_audio_music_sfx"].get("provider_safe_names") or [])
    require({"runway", "kling", "replicate", "openai"}.issubset(visual_names), "Visual category must discover router visual providers.")
    require("elevenlabs" in audio_names, "Audio category must discover router audio providers.")
    require(
        {"internal_ffmpeg_composition"}.issubset(set(proof["discovered_composition_safe_names"])),
        "Composition category must discover internal ffmpeg composition.",
    )
    require(
        {"media_script_caption_plan", "voiceover_script_caption_fallback"}.issubset(set(proof["discovered_caption_safe_names"])),
        "Caption/subtitle category must discover script and voiceover fallback paths.",
    )
    require(
        {"provider_output_or_failure_record", "synthetic_durable_asset_delivery_safe_default", "supportable_failure_path"}.issubset(
            set(proof["discovered_fallback_safe_names"])
        ),
        "Fallback category must discover supportable safe artifact paths.",
    )
    require(
        categories["composition_stitching_internal"].get("selected_method_safe_name") in {"", "internal_ffmpeg_composition"},
        "Composition selection must be an internal safe method name.",
    )
    require(
        "media_script_caption_plan" in set(categories["caption_subtitle_paths"].get("method_safe_names") or []),
        "Caption/subtitle category must expose script caption path.",
    )
    require(
        "provider_output_or_failure_record" in set(categories["fallback_safe_artifact_paths"].get("method_safe_names") or []),
        "Fallback/safe artifact category must expose supportable provider output/failure path.",
    )
    require(
        visual_names.issubset(set(categories["future_registered_provider_stack"].get("provider_safe_names") or [])),
        "Future registered provider stack must include discovered visual providers.",
    )
    env_by_provider = proof.get("required_env_names_by_provider") or {}
    require("runway" in env_by_provider and "RUNWAYML_API_SECRET" in env_by_provider["runway"], "Runway env names must be visible as names only.")
    require("kling" in env_by_provider and {"KLING_API_KEY", "KLING_SECRET_KEY"}.issubset(set(env_by_provider["kling"])), "Kling env names must be visible as names only.")
    require("elevenlabs" in env_by_provider and "ELEVENLABS_API_KEY" in env_by_provider["elevenlabs"], "ElevenLabs env name must be visible as a name only.")
    provider_matrix = proof.get("complete_media_executable_provider_matrix_redacted") or []
    require(provider_matrix, "Complete media executable provider matrix must be present.")
    matrix_names = {item.get("provider_safe_name") for item in provider_matrix}
    for expected_name in {
        "runway",
        "kling",
        "heygen",
        "replicate",
        "openai",
        "sync",
        "elevenlabs",
        "internal_ffmpeg_composition",
        "media_script_caption_plan",
        "voiceover_script_caption_fallback",
        "provider_output_or_failure_record",
        "synthetic_durable_asset_delivery_safe_default",
        "supportable_failure_path",
    }:
        require(expected_name in matrix_names, f"Provider matrix missing safe entry: {expected_name}")
    for item in provider_matrix:
        require(item.get("credential_values_exposed") is False, f"Provider matrix must not expose credentials: {item.get('provider_safe_name')}")
        for env_record in list(item.get("env_present_redacted") or []):
            require("env_name" in env_record, "Env record must expose env variable name only.")
            require("env_present" in env_record and "value_length_present" in env_record, "Env record must expose redacted presence booleans.")
            require("credential_values_exposed" in env_record and env_record["credential_values_exposed"] is False, "Env record must not expose credential values.")
    if proof["proof_blocked_reason"] == "provider_category_readiness_not_verified":
        require(
            proof["provider_category_readiness_verified"] is False,
            "Category readiness blocker must mean category readiness is false.",
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
        "provider" in proof["next_operator_action"].lower(),
        "Next operator action must name the provider readiness or approval action needed.",
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
        "provider_call_count=0",
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
        "provider_router_used": proof.get("provider_router_used"),
        "provider_pair_hardcoded": proof.get("provider_pair_hardcoded"),
        "selected_visual_provider_safe_name": proof.get("selected_visual_provider_safe_name"),
        "selected_audio_provider_safe_name": proof.get("selected_audio_provider_safe_name"),
        "selected_composition_method_safe_name": proof.get("selected_composition_method_safe_name"),
        "selected_caption_method_safe_name": proof.get("selected_caption_method_safe_name"),
        "selected_fallback_artifact_method_safe_name": proof.get("selected_fallback_artifact_method_safe_name"),
        "full_media_stack_mapping_attempted": proof.get("full_media_stack_mapping_attempted"),
        "full_media_stack_mapping_passed": proof.get("full_media_stack_mapping_passed"),
        "dotenv_local_loaded": proof.get("dotenv_local_loaded"),
        "dotenv_values_exposed": proof.get("dotenv_values_exposed"),
        "env_values_exposed": proof.get("env_values_exposed"),
        "provider_environment_readiness_attempted": proof.get("provider_environment_readiness_attempted"),
        "provider_environment_readiness_passed": proof.get("provider_environment_readiness_passed"),
        "provider_category_readiness_attempted": proof.get("provider_category_readiness_attempted"),
        "caption_or_subtitle_path_ready_or_not_required": proof.get("caption_or_subtitle_path_ready_or_not_required"),
        "fallback_safe_artifact_path_ready": proof.get("fallback_safe_artifact_path_ready"),
        "discovered_visual_provider_safe_names": proof.get("discovered_visual_provider_safe_names"),
        "discovered_audio_provider_safe_names": proof.get("discovered_audio_provider_safe_names"),
        "discovered_composition_safe_names": proof.get("discovered_composition_safe_names"),
        "discovered_caption_safe_names": proof.get("discovered_caption_safe_names"),
        "discovered_fallback_safe_names": proof.get("discovered_fallback_safe_names"),
        "visual_provider_readiness_verified": proof.get("visual_provider_readiness_verified"),
        "audio_provider_readiness_verified": proof.get("audio_provider_readiness_verified"),
        "visual_provider_category_ready": proof.get("visual_provider_category_ready"),
        "audio_provider_category_ready": proof.get("audio_provider_category_ready"),
        "composition_method_ready": proof.get("composition_method_ready"),
        "provider_category_readiness_verified": proof.get("provider_category_readiness_verified"),
        "provider_call_count": proof.get("provider_call_count"),
        "visual_provider_call_count": proof.get("visual_provider_call_count"),
        "audio_provider_call_count": proof.get("audio_provider_call_count"),
        "provider_retry_count": proof.get("provider_retry_count"),
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
