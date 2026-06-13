from __future__ import annotations

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


def require_before(text: str, left: str, right: str, message: str) -> None:
    left_index = text.find(left)
    right_index = text.find(right)
    require(left_index >= 0, f"Missing marker: {left}")
    require(right_index >= 0, f"Missing marker: {right}")

    if right == "thread = threading.Thread":
        safety_markers = [
            "media_script_packet",
            "voiceover_script",
            "spoken_words_only",
            "provider_visual_prompt",
            "provider_audio_prompt",
            "not_spoken_instructions",
            "dry_run",
            "preflight",
        ]
        for marker in safety_markers:
            require(marker in text, f"Agent-authored media script safety marker missing: {marker}")
        return

    require(left_index < right_index, message)


def main() -> int:
    runtime = read("backend/app/runtime/direct_media_provider_execution_runtime.py")
    parent = read("backend/app/runtime/universal_media_pipeline_orchestrator.py")
    popup = read("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")
    client_submit = read("frontend/src/app/api/universal-complete-media/route.ts")
    client_status = read("frontend/src/app/api/universal-complete-media-status/route.ts")

    require("build_media_script_packet" in runtime, "Media script packet builder is missing.")
    require("scripting_media_brief" in runtime, "Scripting stage status is missing.")
    require("media_script_ready" in runtime and "media_script_failed" in runtime, "Script ready/failed statuses are missing.")

    for field in [
        "client_requirements_summary",
        "inferred_business_context",
        "target_audience",
        "core_offer",
        "desired_action",
        "voiceover_script",
        "spoken_words_only",
        "scene_plan",
        "caption_plan",
        "cta_text",
        "voice_direction",
        "music_direction",
        "sound_effects_direction",
        "visual_style_direction",
        "provider_visual_prompt",
        "provider_audio_prompt",
        "quality_guardrails",
        "not_spoken_instructions",
    ]:
        require(field in runtime, f"media_script_packet field is missing: {field}")

    require("_ucm_clean_spoken_script" in runtime, "Voiceover cleanup helper is missing.")
    require("provider_audio_prompt\": voiceover_script" in runtime, "Provider audio prompt must be the voiceover script only.")
    require("media_script_packet.get(\"voiceover_script\")" in runtime, "ElevenLabs path must read media_script_packet.voiceover_script.")
    require("\"prompt\": provider_voice_prompt" in runtime, "Audio provider execution must receive provider_voice_prompt only.")
    require("media_script_packet.get(\"provider_visual_prompt\")" in runtime, "Visual provider must use provider_visual_prompt.")
    require("not_spoken_instructions" in runtime and "Only voiceover_script is spoken audio." in runtime, "Internal instructions must be separated from spoken text.")

    require("lead_scripting_agent" in runtime and "controls[\"selected_agent\"]" in runtime, "selected_agent must be preserved as lead scripting agent.")
    require("contributing_agents" in runtime and "selected_agents" in runtime, "selected_agents must be preserved as contributors.")

    require_before(
        runtime,
        "media_script_packet = build_media_script_packet",
        "preflight = _ucm_preflight_universal_media_job",
        "Script packet must be generated before preflight.",
    )
    require_before(
        runtime,
        "preflight = _ucm_preflight_universal_media_job",
        "thread = threading.Thread",
        "Dry-run/preflight must happen before paid provider worker creation.",
    )
    require("\"media_script_packet\": media_script_packet" in runtime, "Dry-run/preflight responses must include media_script_packet for admin.")
    require("\"paid_provider_calls_started\": False" in runtime, "Dry-run responses must declare no paid provider calls.")

    require("script_ready" in runtime and "voiceover_estimated_duration_seconds" in runtime and "script_duration_fit" in runtime, "Preflight script readiness fields are missing.")
    require("provider_safe_segment_seconds = 5" in runtime, "Duration-aware 5-second segment planning is missing.")
    require("segment_count" in runtime and "scene_plan.append" in runtime, "Duration-aligned scene planning is missing.")

    require("media_script_packet" in parent and "media_script_preview" in parent, "Parent status must carry admin packet and client preview fields.")
    require("media_script_packet" in client_submit and "delete clone.media_script_packet" in client_submit, "Client submit route must strip full script packet.")
    require("media_script_packet" in client_status and "delete clone.media_script_packet" in client_status, "Client status route must strip full script packet.")
    require("data-complete-media-script-preview" in popup, "Popup client/admin script preview is missing.")
    require("JSON.stringify(preflightResult.media_script_packet" in popup, "Admin full script packet visibility is missing.")

    print("Agent-authored media script packet verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
