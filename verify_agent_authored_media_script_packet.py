from __future__ import annotations

import ast
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


def require_tone_references_are_safe(runtime: str) -> None:
    tree = ast.parse(runtime)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        references_tone = any(
            isinstance(child, ast.Name) and child.id == "tone" and isinstance(child.ctx, ast.Load)
            for child in ast.walk(node)
        )
        if not references_tone:
            continue

        args = {arg.arg for arg in node.args.args}
        local_assignments = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        local_assignments.add(target.id)
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                local_assignments.add(child.target.id)
            elif isinstance(child, ast.NamedExpr) and isinstance(child.target, ast.Name):
                local_assignments.add(child.target.id)

        require(
            "tone" in args or "tone" in local_assignments,
            f"Function {node.name} references tone without receiving or defining it.",
        )


def load_runtime_module():
    path = ROOT / "backend/app/runtime/direct_media_provider_execution_runtime.py"
    spec = importlib.util.spec_from_file_location("agent_script_runtime_under_test", path)
    if not spec or not spec.loader:
        raise AssertionError("Could not load direct media runtime module spec.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_complete_voiceover_endings() -> None:
    module = load_runtime_module()
    dangling_fragments = [
        "Book your free",
        "Book your",
        "Get your",
        "Request a",
        "Contact us for",
        "Start your",
    ]

    payload = {
        "prompt": "Create a 10s no-human epoxy flooring ad for dull concrete.",
        "business_name": "Prime Epoxy Floors",
        "product_or_service": "epoxy flooring",
        "audience": "homeowners and trade business owners",
        "goal": "book free quote enquiries",
        "duration_seconds": 10,
        "human_avatar_mode": "No human/avatar",
        "call_to_action": "Book your free quote today",
    }
    packet = module.build_media_script_packet(payload, {"duration_seconds": 10})
    voiceover = str(packet.get("voiceover_script") or "").strip()
    require(voiceover, "10s epoxy voiceover must be generated.")
    require(voiceover[-1] in ".!?", f"Voiceover must end with a complete sentence: {voiceover}")
    for fragment in dangling_fragments:
        require(
            not voiceover.rstrip(" .!?").endswith(fragment),
            f"Voiceover ends with dangling CTA fragment {fragment!r}: {voiceover}",
        )
    require(
        "Book your free quote today." in voiceover or "Book your free" not in voiceover,
        f"Voiceover must include a full CTA or omit it cleanly: {voiceover}",
    )
    require(
        packet.get("provider_audio_prompt") == packet.get("voiceover_script"),
        "provider_audio_prompt must remain exactly voiceover_script.",
    )

    truncated = module._ucm_clean_spoken_script(
        "Tired of dull, stained concrete? Upgrade to epoxy flooring that looks sharp, lasts longer, and is easy to clean. Book your free quote today.",
        22,
    )
    for fragment in dangling_fragments:
        require(
            not truncated.rstrip(" .!?").endswith(fragment),
            f"Cleaner must not leave dangling CTA fragment {fragment!r}: {truncated}",
        )


def main() -> int:
    runtime = read("backend/app/runtime/direct_media_provider_execution_runtime.py")
    parent = read("backend/app/runtime/universal_media_pipeline_orchestrator.py")
    popup = read("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")
    client_submit = read("frontend/src/app/api/universal-complete-media/route.ts")
    client_status = read("frontend/src/app/api/universal-complete-media-status/route.ts")

    require("build_media_script_packet" in runtime, "Media script packet builder is missing.")
    require("scripting_media_brief" in runtime, "Scripting stage status is missing.")
    require("media_script_ready" in runtime and "media_script_failed" in runtime, "Script ready/failed statuses are missing.")
    require_tone_references_are_safe(runtime)
    require(
        'tone = controls.get("tone") or "natural, confident, professional, warm"' in runtime,
        "Runtime must define tone locally with the production fallback before using it in script packet generation.",
    )
    require_complete_voiceover_endings()

    for bad_phrase in [
        "Generate quote enquiries",
        "helps Homeowners, trades businesses",
        "You get Free",
        "f\"{business_name} helps {audience}",
        "f\"You get {offer}",
        "caption_text\": spoken_chunk",
        "script = f\"{script} {must_include}.\"",
        "script = f\"{script} {include_value}.\"",
        "{must_include}.",
        "str(must_include",
        "else \"homeowner or trade business owner booking a free quote\"",
    ]:
        require(bad_phrase not in runtime, f"Robotic or unsafe script pattern remains in runtime: {bad_phrase}")

    for dangling_fragment in [
        "Book your free",
        "Book your",
        "Get your",
        "Request a",
        "Contact us for",
        "Start your",
    ]:
        require(dangling_fragment in runtime, f"Dangling CTA fragment guard is missing: {dangling_fragment}")

    for helper in [
        "_ucm_humanize_audience",
        "_ucm_convert_goal_to_customer_benefit",
        "_ucm_build_service_ad_voiceover",
        "_ucm_build_marketing_caption_plan",
        "_ucm_build_scene_specific_visual_plan",
        "_ucm_natural_must_include_benefits",
        "_ucm_weave_benefits_into_voiceover",
        "_ucm_no_human_or_product_led_mode",
        "_ucm_human_avatar_mode_kind",
        "_ucm_human_led_final_cta_scene",
        "_ucm_uploaded_likeness_consent_present",
        "_ucm_ends_with_dangling_cta_fragment",
        "_ucm_sentence_safe_word_trim",
    ]:
        require(f"def {helper}" in runtime, f"Creative-quality helper is missing: {helper}")

    for mode in [
        "No human/avatar",
        "Generate new avatar/person",
        "Use client-uploaded face/likeness",
        "Use saved brand spokesperson/avatar",
    ]:
        require(mode in runtime, f"Locked human/avatar mode is missing from runtime: {mode}")
        require(mode in popup, f"Locked human/avatar mode is missing from popup: {mode}")

    require(
        "_ucm_natural_must_include_benefits(controls.get(\"must_include\"), max_items=2)" in runtime,
        "must_include must be converted into concise natural benefits before voiceover use.",
    )
    require(
        "_ucm_weave_benefits_into_voiceover(script, benefits, max_words)" in runtime,
        "must_include benefits must be woven into voiceover under the word budget.",
    )

    for phrase in [
        "dull, stained concrete",
        "epoxy flooring",
        "easy to clean",
        "free quote",
    ]:
        require(phrase in runtime, f"Epoxy-specific positive language is missing: {phrase}")

    for overlay in [
        "Dull concrete?",
        "Premium epoxy flooring",
        "Proper surface preparation",
        "Durable. Glossy. Easy to clean.",
        "Book your free quote today",
    ]:
        require(overlay in runtime, f"Marketing-overlay caption copy is missing: {overlay}")

    require(
        "_ucm_build_marketing_caption_plan(controls, duration, segment_count)" in runtime,
        "Caption generation must use marketing overlays instead of raw narration chunking.",
    )
    require(
        "_ucm_build_scene_specific_visual_plan(controls, voiceover_script, duration, segment_count)" in runtime,
        "Scene generation must use scene-specific visual planning.",
    )
    require(
        "final polished epoxy floor reveal with CTA text and no people" in runtime,
        "No-human/product-led epoxy mode must use a final floor reveal with CTA text and no people.",
    )
    require(
        "if _ucm_no_human_or_product_led_mode(controls)" in runtime,
        "Epoxy CTA scene must check human/avatar mode before showing people.",
    )
    require(
        "_ucm_human_led_final_cta_scene(controls)" in runtime,
        "Epoxy CTA scene must preserve avatar/person/spokesperson modes through a human-led branch.",
    )
    for human_scene in [
        "human presenter, customer, tradie, or spokesperson booking a free quote",
        "client-uploaded likeness presenter delivering the free quote CTA with consent confirmed",
        "saved brand spokesperson/avatar delivering the free quote CTA",
    ]:
        require(human_scene in runtime, f"Human/avatar CTA scene support is missing: {human_scene}")
    require(
        runtime.find("if _ucm_no_human_or_product_led_mode(controls)") < runtime.find("_ucm_human_led_final_cta_scene(controls)"),
        "Human-led epoxy CTA scene must be guarded by the human/avatar mode check.",
    )

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
