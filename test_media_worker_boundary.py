from __future__ import annotations

import ast
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from backend.app.runtime import background_worker_loop
from backend.app.runtime import async_media_job_foundation as media_jobs
from backend.app.runtime import durable_execution_queue_runtime as durable_queue


ROOT = Path(__file__).resolve().parent
RUN_ALL_ROUTE = ROOT / "frontend/src/app/api/admin-media-jobs-run-all/route.ts"
RUN_NEXT_ROUTE = ROOT / "frontend/src/app/api/admin-media-jobs-run-next/route.ts"
BACKEND_MAIN = ROOT / "backend/app/main.py"
MEDIA_FOUNDATION = ROOT / "backend/app/runtime/async_media_job_foundation.py"
WORKER_LOOP = ROOT / "backend/app/runtime/background_worker_loop.py"
RENDER_YAML = ROOT / "render.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _function_source(path: Path, name: str) -> str:
    source = _read(path)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Function not found: {name}")


def _function_body_source(path: Path, name: str) -> str:
    source = _read(path)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return "\n".join(ast.get_source_segment(source, item) or "" for item in node.body)
    raise AssertionError(f"Function not found: {name}")


def _json_text(value: Any) -> str:
    return str(value).lower()


def _unsafe_fast_packet_markers() -> list[str]:
    return [
        "you are executing as",
        "platform standard",
        "output quality requirement",
        "agent-specific behaviour",
        "required structure",
        "create operational execution task",
        "run delegated workforce",
        "wait for generated media assets",
        "super_secret",
        "internal_prompt",
    ]


def test_frontend_uses_trigger_routes_only() -> None:
    run_all = _read(RUN_ALL_ROUTE)
    run_next = _read(RUN_NEXT_ROUTE)

    assert "/admin/media-jobs/run-all" not in run_all
    assert "/admin/media-jobs/trigger-all" in run_all
    assert "/admin/media-jobs/run-next" not in run_next
    assert "/admin/media-jobs/trigger-next" in run_next

    for route in [run_all, run_next]:
        assert "adminPortalAuthorised(req)" in route
        assert "background_processor_scheduled" in route
        assert "request_path_safe" in route
        assert "frontend_proxy/backend_trigger_only" in route


def test_backend_trigger_routes_are_queue_only() -> None:
    main = _read(BACKEND_MAIN)
    assert '@app.post("/admin/media-jobs/trigger-all")' in main
    assert '@app.post("/admin/media-jobs/trigger-next")' in main

    forbidden = [
        "run_all_media_jobs(",
        "run_next_media_job(",
        "process_media_job(",
        "process_queued_creative_media_jobs(",
        "generate_creative_media_pack(",
        "execute_ai_media_provider_ready_packet",
        "run_runway_text_to_video_quality_test",
        "run_elevenlabs_tts_quality_test",
        "subprocess",
        "ffmpeg",
        "pip install",
    ]
    for function_name in [
        "admin_trigger_all_media_jobs",
        "admin_trigger_next_media_job",
        "admin_run_all_media_jobs",
        "admin_run_next_media_job",
    ]:
        body = _function_body_source(BACKEND_MAIN, function_name)
        for marker in forbidden:
            assert marker not in body, f"{function_name} contains web-path execution marker {marker}"

    trigger_response = _function_source(BACKEND_MAIN, "_media_job_trigger_response")
    assert "triggered" in trigger_response
    assert "background_processor_scheduled" in trigger_response
    assert "request_path_safe" in trigger_response
    assert "provider_result" not in trigger_response
    assert "provider_response" not in trigger_response


def test_list_media_jobs_is_fast_local_by_default() -> None:
    function_source = _function_source(MEDIA_FOUNDATION, "list_media_jobs")
    signature = function_source.splitlines()[0]
    assert "reconcile_visible_assets: bool = False" in signature

    body = _function_body_source(MEDIA_FOUNDATION, "list_media_jobs")
    assert "get_persisted_creative_assets" not in body
    assert "canonical_list_media_assets" not in body
    assert "supabase" not in body.lower()
    assert "postgres" not in body.lower()

    trigger_all = _function_body_source(MEDIA_FOUNDATION, "trigger_all_creative_media_jobs")
    trigger_next = _function_body_source(MEDIA_FOUNDATION, "trigger_next_creative_media_job")
    assert "reconcile_visible_queued_media_asset_jobs" not in trigger_all
    assert "reconcile_visible_queued_media_asset_jobs" not in trigger_next

    old_store = media_jobs.STORE
    old_reconcile = media_jobs.reconcile_visible_queued_media_asset_jobs

    def blocked_reconciliation(*args, **kwargs):
        raise AssertionError("default list path attempted live reconciliation")

    with TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        media_jobs.reconcile_visible_queued_media_asset_jobs = blocked_reconciliation
        try:
            result = media_jobs.list_media_jobs(limit=10)
            assert result["success"] is True
            assert result["job_count"] == 0
        finally:
            media_jobs.reconcile_visible_queued_media_asset_jobs = old_reconcile
            media_jobs.STORE = old_store


def test_durable_queue_bridge_is_global_and_secret_safe() -> None:
    foundation = _read(MEDIA_FOUNDATION)
    assert 'CREATIVE_MEDIA_GENERATION_QUEUE = "creative_media_generation_queue"' in foundation
    assert "enqueue_creative_media_job_for_worker" in foundation
    assert "trigger_all_creative_media_jobs" in foundation
    assert "trigger_next_creative_media_job" in foundation

    bridge_source = "\n".join(
        [
            _function_source(MEDIA_FOUNDATION, "_durable_media_queue_payload"),
            _function_source(MEDIA_FOUNDATION, "enqueue_creative_media_job_for_worker"),
            _function_source(MEDIA_FOUNDATION, "trigger_all_creative_media_jobs"),
            _function_source(MEDIA_FOUNDATION, "trigger_next_creative_media_job"),
        ]
    ).lower()
    assert "ugc" not in bridge_source
    assert "creative_media_generation_queue" in bridge_source
    assert "process_media_job(" not in bridge_source
    assert "generate_creative_media_pack(" not in bridge_source
    assert "fast_creative_media_output_packet" in _read(MEDIA_FOUNDATION)

    payload = media_jobs._durable_media_queue_payload(
        {
            "job_id": "media_job_boundary_001",
            "task": "Create media",
            "agent_id": "product_image_agent",
            "tenant_id": "client_demo",
            "provider_token": "secret",
            "api_key": "secret",
            "internal_prompt": "hidden",
        }
    )
    payload_text = str(payload).lower()
    assert payload["queue_name"] == "creative_media_generation_queue"
    assert payload["agent_id"] == "product_image_agent"
    assert "secret" not in payload_text
    assert "api_key" not in payload_text
    assert "provider_token" not in payload_text
    assert "internal_prompt" not in payload_text


def test_fast_packet_sanitises_internal_and_operational_text() -> None:
    unsafe_job = {
        "job_id": "media_job_internal_prompt",
        "status": "queued",
        "agent_id": "paid_ads_agent",
        "tenant_id": "client_demo",
        "task": """
        You are executing as: ugc_creative_agent.
        Platform standard: internal platform policy.
        Output quality requirement: hidden rubric.
        Agent-specific behaviour: private scaffolding.
        Required structure: internal only.
        Create operational execution task for: Next step: Run delegated workforce or wait for generated media assets.
        """,
        "include_video": True,
        "internal_prompt": "super_secret_internal_prompt",
    }
    packet = media_jobs.build_fast_creative_output_packet(unsafe_job)
    packet_text = _json_text(packet)
    assert packet["packet_type"] == "fast_creative_media_status_packet"
    assert packet["fast_output_packet_available"] is False
    assert "hook" not in packet
    assert "caption" not in packet
    assert "creative_brief" not in packet
    for marker in _unsafe_fast_packet_markers():
        assert marker not in packet_text


def test_status_jobs_sanitise_task_scaffolding() -> None:
    old_store = media_jobs.STORE
    unsafe_task = """
    You are executing as: ugc_creative_agent
    Platform standard: internal rules
    Output quality requirement: private rubric
    Agent-specific behaviour: hidden behavior
    Required structure: internal plan
    Customer task: Create one creative media output packet for a premium skincare serum, including a hook, short script, three scene directions, caption, and queued final media render status.
    """
    with TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        try:
            job = media_jobs.enqueue_media_job(
                task=unsafe_task,
                agent_id="creative_product_asset_agent",
                tenant_id="client_demo",
                include_image=True,
                include_video=True,
            )
            listed = media_jobs.list_media_jobs(limit=10)["jobs"][0]
            read = media_jobs.read_media_job(job["job_id"])
        finally:
            media_jobs.STORE = old_store

    for item in [listed, read]:
        text = _json_text(item)
        assert "create one creative media output packet for a premium skincare serum" in text
        assert item["task_summary"] == item["task"]
        assert item["customer_task"] == item["task"]
        for marker in _unsafe_fast_packet_markers():
            assert marker not in text


def test_fast_packet_uses_customer_safe_creative_source_globally() -> None:
    packet = media_jobs.build_fast_creative_output_packet(
        {
            "job_id": "media_job_product_image",
            "status": "queued",
            "agent_id": "product_image_agent",
            "tenant_id": "client_demo",
            "task": "Create a bright product image campaign for a refillable skincare bottle aimed at busy parents.",
            "include_image": True,
            "include_video": False,
        }
    )
    packet_text = _json_text(packet)
    assert packet["packet_type"] == "fast_creative_media_output_packet"
    assert packet["fast_output_packet_available"] is True
    assert "refillable skincare bottle" in packet_text
    assert "product_image_agent" in packet_text
    for marker in _unsafe_fast_packet_markers():
        assert marker not in packet_text


def test_trigger_all_is_bounded_and_does_not_build_large_payloads() -> None:
    old_store = media_jobs.STORE
    old_enqueue = media_jobs.enqueue_creative_media_job_for_worker
    calls: list[str] = []

    def fake_enqueue(job: dict) -> dict:
        calls.append(str(job.get("job_id")))
        return {
            "success": True,
            "status": "queued",
            "triggered": True,
            "background_processor_scheduled": True,
            "queue_name": "creative_media_generation_queue",
            "media_job_id": job.get("job_id"),
            "fast_output_packet_available": True,
            "fast_output_packet": media_jobs.build_fast_creative_output_packet(job),
            "request_path_safe": True,
            "processor_invoked": False,
            "credential_values_exposed": False,
        }

    with TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        media_jobs.enqueue_creative_media_job_for_worker = fake_enqueue
        try:
            for index in range(10):
                media_jobs.enqueue_media_job(
                    task=f"Create product launch creative asset {index}.",
                    agent_id="creative_product_asset_agent",
                    tenant_id="client_demo",
                    include_image=True,
                    include_audio=False,
                    include_video=True,
                )
            result = media_jobs.trigger_all_creative_media_jobs(limit=25)
        finally:
            media_jobs.enqueue_creative_media_job_for_worker = old_enqueue
            media_jobs.STORE = old_store

    assert result["success"] is True
    assert result["request_path_safe"] is True
    assert result["bounded_trigger"] is True
    assert result["request_schedule_limit"] <= 3
    assert result["scheduled_job_count"] == len(calls) <= 3
    assert len(result["fast_output_packets"]) <= 2
    assert result["processor_invoked"] is False


def test_web_trigger_response_exposes_fast_packet_not_final_media() -> None:
    trigger_response = _function_source(BACKEND_MAIN, "_media_job_trigger_response")
    assert "fast_output_packet_available" in trigger_response
    assert "stage_1_fast_creative_response" in trigger_response
    assert "stage_2_async_final_render" in trigger_response
    assert "final_media_completion_claimed" in trigger_response

    foundation = _read(MEDIA_FOUNDATION)
    assert "final_media_completion_claimed" in foundation
    assert "final_asset_status" in foundation


def test_worker_is_the_media_processor_boundary() -> None:
    worker = _read(WORKER_LOOP)
    assert "CREATIVE_MEDIA_GENERATION_QUEUE" in worker
    assert "claim_next_execution_job" in worker
    assert "complete_execution_job" in worker
    assert "retry_execution_job" in worker
    assert "process_one_creative_media_generation_job" in worker

    worker_body = _function_source(WORKER_LOOP, "process_one_creative_media_generation_job")
    assert "process_media_job" in worker_body
    assert "claim_next_execution_job" in worker_body
    assert "dead_letter_execution_job" in worker_body
    assert "provider_response" not in worker_body
    assert "provider_result" not in worker_body


def test_render_worker_service_enables_media_worker_loop() -> None:
    render_yaml = _read(RENDER_YAML)
    assert "name: ecommerce-ai-agent-platform-worker" in render_yaml
    assert "startCommand: python -m backend.app.runtime.background_worker_loop" in render_yaml
    assert "WORKER_LIVE_EXECUTION_ENABLED" in render_yaml
    assert 'value: "true"' in render_yaml


def test_worker_claims_durable_media_queue_and_status_overlay_moves_job_out_of_queued() -> None:
    old_store = media_jobs.STORE
    old_process = media_jobs.process_media_job
    durable_queue.reset_dev_execution_queue_for_tests()

    def fake_process_media_job(job: dict) -> dict:
        return {
            "success": True,
            "processed": True,
            "status": "provider_not_ready",
            "job": {
                "job_id": job.get("job_id"),
                "status": "provider_not_ready",
                "credential_values_exposed": False,
            },
            "credential_values_exposed": False,
        }

    with TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        media_jobs.process_media_job = fake_process_media_job
        import os

        original_env = {key: os.environ.get(key) for key in ["APP_ENV", "DATABASE_URL", "POSTGRES_URL", "RENDER", "PRODUCTION", "WORKER_LIVE_EXECUTION_ENABLED"]}
        os.environ["APP_ENV"] = "development"
        os.environ["WORKER_LIVE_EXECUTION_ENABLED"] = "true"
        os.environ.pop("DATABASE_URL", None)
        os.environ.pop("POSTGRES_URL", None)
        os.environ.pop("RENDER", None)
        os.environ.pop("PRODUCTION", None)
        try:
            job = media_jobs.enqueue_media_job(
                task="Create a product image campaign for a premium serum.",
                agent_id="product_image_agent",
                tenant_id="client_demo",
                include_image=True,
            )
            trigger = media_jobs.enqueue_creative_media_job_for_worker(job)
            assert trigger["queue_name"] == "creative_media_generation_queue"
            worker = background_worker_loop.process_one_creative_media_generation_job()
            assert worker["queue_name"] == "creative_media_generation_queue"
            assert worker["processor_invoked"] is True

            listed = media_jobs.list_media_jobs(limit=10, include_durable_status=True)["jobs"][0]
            assert listed["status"] == "provider_not_ready"
            assert listed["status"] != "queued"
            assert listed["durable_queue_status"] == "completed"
        finally:
            media_jobs.process_media_job = old_process
            media_jobs.STORE = old_store
            durable_queue.reset_dev_execution_queue_for_tests()
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == "__main__":
    test_frontend_uses_trigger_routes_only()
    test_backend_trigger_routes_are_queue_only()
    test_list_media_jobs_is_fast_local_by_default()
    test_durable_queue_bridge_is_global_and_secret_safe()
    test_fast_packet_sanitises_internal_and_operational_text()
    test_status_jobs_sanitise_task_scaffolding()
    test_fast_packet_uses_customer_safe_creative_source_globally()
    test_trigger_all_is_bounded_and_does_not_build_large_payloads()
    test_web_trigger_response_exposes_fast_packet_not_final_media()
    test_worker_is_the_media_processor_boundary()
    test_render_worker_service_enables_media_worker_loop()
    test_worker_claims_durable_media_queue_and_status_overlay_moves_job_out_of_queued()
    print("MEDIA_WORKER_BOUNDARY_PASSED")
