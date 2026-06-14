from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8", errors="ignore")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_runtime_module():
    path = ROOT / "backend/app/runtime/direct_media_provider_execution_runtime.py"
    spec = importlib.util.spec_from_file_location("duration_runtime_under_test", path)
    if not spec or not spec.loader:
        raise AssertionError("Could not load direct media runtime module spec.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    runtime = read("backend/app/runtime/direct_media_provider_execution_runtime.py")
    parent = read("backend/app/runtime/universal_media_pipeline_orchestrator.py")
    popup = read("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")
    client_submit = read("frontend/src/app/api/universal-complete-media/route.ts")
    client_status = read("frontend/src/app/api/universal-complete-media-status/route.ts")

    module = load_runtime_module()
    require(module._ucm_segment_count_for_duration(5, 5) == 1, "5s must map to 1 visual segment.")
    require(module._ucm_segment_count_for_duration(10, 5) == 2, "10s must map to 2 visual segments.")
    require(module._ucm_segment_count_for_duration(25, 5) == 5, "25s must map to 5 visual segments.")
    require(module._ucm_segment_count_for_duration(60, 5) == 12, "60s must map to 12 visual segments.")

    for marker in [
        "requested_duration_seconds",
        "provider_safe_segment_seconds",
        "segment_count",
        "segment_plan",
        "generated_segments",
        "missing_segments",
        "final_duration_seconds",
        "duration_fulfilled",
        "duration_shortfall_seconds",
    ]:
        require(marker in runtime, f"Runtime duration/segment metadata missing: {marker}")
        require(marker in parent, f"Parent status must preserve duration/segment metadata: {marker}")

    require(
        "len(executable_visual) * segment_count" in runtime,
        "Preflight visual paid-call estimate must use segment_count.",
    )
    require(
        "segment_count = 1 if smoke_test_mode" in runtime,
        "Smoke test must remain one segment max 5s.",
    )
    require(
        'safe_payload["duration_seconds"] = 5' in runtime and 'safe_payload["duration"] = 5' in runtime,
        "Smoke test must cap requested duration at 5 seconds.",
    )

    require(
        "_ucm_duration_fulfillment" in runtime and "_ucm_duration_tolerance_seconds" in runtime,
        "Duration fulfillment/tolerance helpers are missing.",
    )
    require(
        '"completed_duration_shortfall"' in runtime and '"composition_duration_shortfall"' in runtime,
        "Duration shortfall statuses are missing.",
    )
    require(
        'final_status = "completed" if fulfillment.get("duration_fulfilled") else "completed_duration_shortfall"' in runtime,
        "Parent must not mark plain completed on major duration shortfall.",
    )

    for marker in [
        '"parent_job_id": parent_job_id',
        '"segment_index": segment.get("segment_index")',
        '"segment_start_seconds": segment.get("segment_start_seconds")',
        '"segment_end_seconds": segment.get("segment_end_seconds")',
        '"segment_prompt": segment.get("segment_prompt")',
        '"provider_job_id": result.get("provider_job_id")',
    ]:
        require(marker in runtime, f"Visual segment child record missing marker: {marker}")

    require(
        'media_script_packet.get("voiceover_script") or ""' in runtime and '"prompt": provider_voice_prompt' in runtime,
        "Audio generation must use media_script_packet.voiceover_script only.",
    )
    require(
        "_ucm_compose_segments_with_sync" in runtime
        and "segment_results"
        in runtime
        and "concat_visual_segments_then_mix_full_voiceover" in runtime,
        "Final composition must reference all generated visual segments.",
    )
    require(
        "ThreadPoolExecutor(max_workers=max_visual_concurrency + 1)" in runtime
        and "max_visual_concurrency = max(1, min(3, len(segment_plan)))" in runtime,
        "Visual segment execution must use controlled concurrency.",
    )

    for marker in [
        "data-complete-media-segment-progress",
        "visual segment",
        "Segment {segment.segmentIndex} of {segment.total}",
        "data-complete-media-segment-row",
        "data-complete-media-audio-row",
        "data-complete-media-composition-row",
        "This can take several minutes because each 5-second visual segment is generated separately",
        "Duration fulfilled",
        "duration_shortfall_seconds",
        "composition_status",
        "audio_status",
    ]:
        require(marker in popup, f"Frontend segment/duration progress UI missing: {marker}")

    for marker in [
        "isPaidMediaConfirmationRequired",
        "universal_complete_media_preflight_blocked",
        "preflight_blocked",
        "acceptable_without_confirmation === false",
        "estimated_credit_risk",
        "data-complete-media-paid-confirmation-required",
        "Paid provider confirmation required",
        "No paid provider calls have started yet",
        "Confirm and run paid media",
        "data-complete-media-confirm-paid-run",
    ]:
        require(marker in popup, f"Frontend high-credit confirmation UI missing: {marker}")

    for marker in [
        "confirmPaidMedia?: boolean",
        "credit_risk_acknowledged: creditRiskAcknowledged",
        "cost_safety_confirmed: Boolean(options.confirmPaidMedia)",
        "paid_provider_risk_confirmed: Boolean(options.confirmPaidMedia)",
        "runCompleteMediaFromPopup({ confirmPaidMedia: true })",
    ]:
        require(marker in popup, f"Confirmed paid-media payload/action missing: {marker}")

    require(
        "result?.success === false && isPaidMediaConfirmationRequired(result)" in popup,
        "HTTP 200 success=false preflight-blocked responses must map to confirmation-required UI.",
    )
    require(
        "Universal complete media request failed with HTTP" not in popup,
        "Popup must not show failed-with-HTTP messaging for preflight confirmation states.",
    )
    for marker in [
        "Generated script preview",
        "Voiceover:",
        "Scene count:",
        "Script fit:",
        "CTA:",
        "Captions:",
        "Human/avatar mode:",
        "Selected creative agent(s):",
        "Show technical script packet",
        "data-complete-media-technical-script-toggle",
        "data-complete-media-technical-script-packet",
        "technicalScriptPacketOpen ?",
    ]:
        require(marker in popup, f"Frontend clean script summary/technical toggle missing: {marker}")
    require(
        "Generated media script packet" not in popup,
        "Popup must not show the old raw packet heading by default.",
    )
    require(
        "portalMode === \"admin\" && preflightResult?.media_script_packet" in popup
        and "JSON.stringify(preflightResult.media_script_packet, null, 2)" in popup,
        "Technical packet JSON must be admin-only and behind the debug toggle.",
    )

    for proxy in [client_submit, client_status]:
        require("segment_prompt" in proxy and "generated_segments" in proxy, "Client proxy must sanitize segment prompt/internal segment data.")

    print("Duration-aware media segment verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
