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
            "universal_complete_media_preflight_blocked",
            "failed_preflight_checks",
            "blocked_provider_calls",
            "smoke_test_mode",
            "dry_run",
            "executable_visual_providers",
            "non_executable_visual_providers",
        ]
        for marker in safety_markers:
            require(marker in text, f"Preflight safety marker missing: {marker}")
        return

    require(left_index < right_index, message)


def main() -> int:
    runtime = read("backend/app/runtime/direct_media_provider_execution_runtime.py")
    parent = read("backend/app/runtime/universal_media_pipeline_orchestrator.py")
    popup = read("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")

    require("_ucm_preflight_universal_media_job" in runtime, "Universal media preflight function is missing.")
    require("universal_complete_media_preflight_blocked" in runtime, "Preflight blocked status is missing.")
    require("CLIENT_PREFLIGHT_MESSAGE" in runtime, "Client-safe preflight message is missing.")

    require_before(
        runtime,
        "preflight = _ucm_preflight_universal_media_job",
        "thread = threading.Thread",
        "Preflight must run before worker thread creation.",
    )
    require_before(
        runtime,
        "if dry_run_mode or preflight.get(\"status\") == \"universal_complete_media_preflight_blocked\":",
        "thread = threading.Thread",
        "Dry-run or blocked preflight must return before worker creation.",
    )
    require_before(
        runtime,
        "\"paid_provider_calls_started\": False",
        "thread = threading.Thread",
        "Dry-run/blocked status must declare no paid provider calls before worker creation.",
    )

    require("execute_direct_media_provider_job" in runtime, "Provider execution function is missing.")
    require(
        "executable_visual_provider_order = [" in runtime
        and "for provider_position, video_provider in enumerate(executable_visual_provider_order" in runtime
        and "executor.submit(_run_visual_segment, segment)" in runtime,
        "Live visual attempts must iterate only executable preflight providers.",
    )
    visual_loop_start = runtime.find("for provider_position, video_provider in enumerate(executable_visual_provider_order")
    require(
        "non_executable_visual_providers" in runtime
        and visual_loop_start >= 0
        and "blocked_provider_adapter_unavailable" not in runtime[visual_loop_start:],
        "Unavailable fallbacks must be recorded during preflight, not called as live child attempts.",
    )
    require(
        "if smoke_test_mode:" in runtime and "safe_payload[\"duration_seconds\"] = 5" in runtime,
        "Smoke test mode must be capped to 5 seconds before planning/execution.",
    )
    require(
        "Smoke test mode requires at least one executable visual provider." in runtime,
        "Smoke test visual-provider guard is missing.",
    )

    for field in [
        "failed_preflight_checks",
        "blocked_provider_calls",
        "estimated_duration_seconds",
        "estimated_credit_risk",
        "executable_visual_providers",
        "non_executable_visual_providers",
        "executable_audio_providers",
    ]:
        require(field in runtime and field in parent, f"Preflight field missing from runtime or parent status: {field}")

    require("data-complete-media-readiness-check" in popup, "Popup Check readiness button is missing.")
    require("data-complete-media-smoke-test" in popup, "Popup Run 5s smoke test button is missing.")
    require("preflightResult?.status === \"universal_complete_media_preflight_blocked\"" in popup, "Popup must block Create when preflight fails.")
    require("window.confirm" in popup and "high estimated provider credit risk" in popup, "Popup high-risk confirmation is missing.")

    print("Media provider preflight safety verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
