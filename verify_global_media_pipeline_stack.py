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


def main() -> int:
    main_py = read("backend/app/main.py")
    orchestrator = read("backend/app/runtime/universal_media_pipeline_orchestrator.py")
    direct_runtime = read("backend/app/runtime/direct_media_provider_execution_runtime.py")
    admin_route = read("frontend/src/app/api/admin-universal-complete-media/route.ts")
    client_submit_route = read("frontend/src/app/api/universal-complete-media/route.ts")
    client_status_route = read("frontend/src/app/api/universal-complete-media-status/route.ts")
    admin_diag_route = read("frontend/src/app/api/admin-runway-key-diagnostics/route.ts")
    popup = read("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx")

    require("/admin/universal-complete-media" in main_py, "Backend universal parent submit route is missing.")
    require("accept_universal_media_pipeline_job" in main_py, "Backend submit route must use the durable parent orchestrator.")
    require("accept_universal_media_pipeline_job" in orchestrator, "Universal parent accept function is missing.")

    require("/admin/universal-complete-media-status" in main_py, "Backend universal status route is missing.")
    require("job_id" in admin_route, "Admin status route must accept job_id.")
    require("get_universal_media_pipeline_status" in main_py, "Backend status route must read the durable parent status.")
    require("durable_parent_job_missing" in orchestrator, "Missing clear durable parent not-found status.")
    require("direct_store_recovered" not in orchestrator, "Universal status must not fall back to direct jobs as the source of truth.")

    require("/admin/direct-media-provider-job-status" in main_py, "Direct child job status backend route is missing.")
    require("admin-direct-media-provider-job-status" in popup, "Popup must still be able to inspect direct child jobs.")

    for field in [
        "child_jobs",
        "visual_attempts",
        "failed_provider_attempts",
        "selected_video_job_id",
        "provider_attempt_count",
        "visual_attempt_count",
    ]:
        if field == "visual_attempts":
            ok = (
                ("visual_attempts" in direct_runtime or "visual_attempts" in orchestrator)
                and "child_jobs" in direct_runtime
                and "child_jobs" in orchestrator
            )
        else:
            ok = field in direct_runtime and field in orchestrator

        require(ok, f"Fallback/status field missing from payload shape: {field}")

    require("runway_safe_key_diagnostics" in direct_runtime, "Safe Runway diagnostics helper is missing.")
    require("/admin/runway-key-diagnostics" in main_py, "Backend admin Runway diagnostics route is missing.")
    require((ROOT / "frontend/src/app/api/admin-runway-key-diagnostics/route.ts").exists(), "Frontend admin diagnostics route is missing.")
    require("sha256_prefix" in direct_runtime, "Runway diagnostics must include a safe sha256 prefix.")
    require("used_env_name" in direct_runtime, "Runway diagnostics must state which env var is used.")
    require("starts_with" not in direct_runtime, "Runway diagnostics must not expose credential prefixes.")

    admin_client_distinction_ok = (
        (
            "audience=\"admin\"" in main_py
            or "audience = \"admin\"" in main_py
            or "audience='admin'" in main_py
            or "audience = 'admin'" in main_py
            or "\"admin\"" in main_py
        )
        and (
            "audience=\"client\"" in main_py
            or "audience = \"client\"" in main_py
            or "audience='client'" in main_py
            or "audience = 'client'" in main_py
            or "\"client\"" in main_py
        )
        and (
            "get_universal_media_pipeline_status" in main_py
            or "universal-complete-media-status" in main_py
        )
    )
    require(admin_client_distinction_ok, "Admin/client status distinction is missing.")
    require("clientSafeStatusPayload" in client_status_route, "Client status route must sanitize admin diagnostics.")
    require("clientSafePayload" in client_submit_route, "Client submit route must sanitize admin diagnostics.")
    require("admin_provider_diagnostics" in orchestrator, "Admin diagnostics field is missing from admin payload shape.")

    require((ROOT / "frontend/src/app/api/admin-universal-complete-media/route.ts").exists(), "Admin frontend route exists.")
    require((ROOT / "frontend/src/app/api/universal-complete-media-status/route.ts").exists(), "Client frontend status route exists.")
    require((ROOT / "frontend/src/app/api/universal-complete-media/route.ts").exists(), "Client frontend submit route exists.")
    require("UniversalCompleteMediaRunAgentPanel" in popup, "Create Media popup component is missing.")
    require("multi_agent_media_execution" in popup and "selected_agents" in popup, "Popup multi-agent payload fields are missing.")

    print("Global media pipeline stack verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
