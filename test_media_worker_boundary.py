from __future__ import annotations

import ast
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from backend.app.runtime import background_worker_loop
from backend.app.runtime import admin_creative_media_asset_viewer as asset_viewer
from backend.app.runtime import async_media_job_foundation as media_jobs
from backend.app.runtime import creative_asset_persistence_bridge as creative_assets
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
        "this is a unique multi-agent, multi-industry platform",
        "do not default to ecommerce",
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


def test_durable_queue_claim_sql_qualifies_returning_columns_and_claims_queue() -> None:
    claim_source = _function_source(ROOT / "backend/app/runtime/durable_execution_queue_runtime.py", "claim_next_execution_job")
    assert "FOR UPDATE SKIP LOCKED" in claim_source
    assert 'RETURNING {_select_columns_for_alias("job")}' in claim_source
    assert "RETURNING {_select_columns()}" not in claim_source
    assert "WHERE job.job_id = candidate.job_id" in claim_source
    assert durable_queue._select_columns_for_alias("job").split(", ")[0] == "job.job_id"

    durable_queue.reset_dev_execution_queue_for_tests()
    import os

    original_env = {key: os.environ.get(key) for key in ["APP_ENV", "DATABASE_URL", "POSTGRES_URL", "RENDER", "PRODUCTION"]}
    os.environ["APP_ENV"] = "development"
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("POSTGRES_URL", None)
    os.environ.pop("RENDER", None)
    os.environ.pop("PRODUCTION", None)
    try:
        enqueue = durable_queue.enqueue_execution_job(
            queue_name="creative_media_generation_queue",
            tenant_id="client_demo",
            project_id="creative_media",
            agent_id="creative_media_agent",
            action_type="creative_media_generation_job",
            payload={
                "media_job_id": "media_job_claim_sql_test",
                "job_id": "media_job_claim_sql_test",
                "task": "Create one safe creative media status packet.",
                "credential_values_exposed": False,
            },
            idempotency_key="test:media_job_claim_sql_test",
        )
        assert enqueue["success"] is True
        claim = durable_queue.claim_next_execution_job(queue_name="creative_media_generation_queue", worker_id="test_worker")
        assert claim["success"] is True
        assert claim["status"] == "leased"
        assert claim["job"]["queue_name"] == "creative_media_generation_queue"
        assert claim["job"]["job_id"] == enqueue["job_id"]
    finally:
        durable_queue.reset_dev_execution_queue_for_tests()
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_background_worker_entrypoint_defines_media_processor_before_main_runs() -> None:
    worker = _read(WORKER_LOOP)
    processor_index = worker.index("def process_one_creative_media_generation_job")
    entrypoint_index = worker.index('if __name__ == "__main__":')
    assert processor_index < entrypoint_index
    assert hasattr(background_worker_loop, "process_one_creative_media_generation_job")

    old_processor = background_worker_loop.process_one_creative_media_generation_job
    import os

    original = os.environ.get("WORKER_LIVE_EXECUTION_ENABLED")

    def fake_process_one() -> dict:
        return {
            "success": True,
            "queue_name": "creative_media_generation_queue",
            "status": "empty",
            "processor_invoked": False,
            "credential_values_exposed": False,
        }

    os.environ["WORKER_LIVE_EXECUTION_ENABLED"] = "true"
    background_worker_loop.process_one_creative_media_generation_job = fake_process_one
    try:
        result = background_worker_loop.run_once()
    finally:
        background_worker_loop.process_one_creative_media_generation_job = old_processor
        if original is None:
            os.environ.pop("WORKER_LIVE_EXECUTION_ENABLED", None)
        else:
            os.environ["WORKER_LIVE_EXECUTION_ENABLED"] = original

    assert result["success"] is True
    assert result["queue_name"] == "creative_media_generation_queue"


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


def test_worker_outcome_remains_visible_without_local_media_job_json() -> None:
    old_store = media_jobs.STORE
    durable_queue.reset_dev_execution_queue_for_tests()
    import os

    original_env = {key: os.environ.get(key) for key in ["APP_ENV", "DATABASE_URL", "POSTGRES_URL", "RENDER", "PRODUCTION"]}
    os.environ["APP_ENV"] = "development"
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("POSTGRES_URL", None)
    os.environ.pop("RENDER", None)
    os.environ.pop("PRODUCTION", None)

    with TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        try:
            enqueue = durable_queue.enqueue_execution_job(
                queue_name="creative_media_generation_queue",
                tenant_id="client_demo",
                project_id="creative_media",
                agent_id="creative_product_asset_agent",
                action_type="creative_media_generation_job",
                payload={
                    "media_job_id": "media_job_missing_local_json",
                    "job_id": "media_job_missing_local_json",
                    "task": "Create one creative media output packet for a premium skincare serum.",
                    "agent_id": "creative_product_asset_agent",
                    "tenant_id": "client_demo",
                },
                idempotency_key="test:media_job_missing_local_json",
            )
            claim = durable_queue.claim_next_execution_job(queue_name="creative_media_generation_queue", worker_id="test_worker")
            assert claim["status"] == "leased"
            durable_queue.complete_execution_job(
                enqueue["job_id"],
                worker_id="test_worker",
                result={
                    "media_job_id": "media_job_missing_local_json",
                    "media_job_status": "provider_not_ready",
                    "processed": True,
                    "provider_status": "provider_not_ready",
                    "asset_count": 0,
                    "playable_asset_count": 0,
                    "preview_ready_count": 0,
                    "download_ready_count": 0,
                    "final_asset_ids": [],
                    "safe_visible_reason": "Provider execution is not currently available.",
                    "credential_values_exposed": False,
                },
            )

            status = media_jobs.list_media_jobs(limit=10, include_durable_status=True)
            assert status["job_count"] == 1
            job = status["jobs"][0]
            assert job["media_job_id"] == "media_job_missing_local_json"
            assert job["durable_queue_job_id"] == enqueue["job_id"]
            assert job["status"] == "provider_not_ready"
            assert job["worker_claimed"] is True
            assert job["worker_completed"] is True
            assert job["asset_count"] == 0
            assert job["playable_asset_count"] == 0
            assert "skincare serum" in _json_text(job)
            for marker in _unsafe_fast_packet_markers():
                assert marker not in _json_text(job)

            assets = asset_viewer.get_admin_creative_media_assets(limit=10)
            assert assets["success"] is True
            evidence = [item for item in assets["assets"] if item.get("media_job_id") == "media_job_missing_local_json"]
            assert evidence
            assert evidence[0]["durable_queue_job_id"] == enqueue["job_id"]
            assert evidence[0]["playable"] is False
        finally:
            media_jobs.STORE = old_store
            durable_queue.reset_dev_execution_queue_for_tests()
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


def test_asset_viewer_sanitises_operational_asset_content_without_changing_playability() -> None:
    unsafe_asset = {
        "asset_id": "asset_operational_text",
        "agent_id": "creative_media_agent",
        "provider": "internal",
        "asset_type": "audio",
        "status": "persisted",
        "playable": True,
        "preview_ready": True,
        "download_ready": True,
        "metadata_only": False,
        "provider_asset_url": "https://demo.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
        "preview_url": "https://demo.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
        "download_url": "https://demo.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
        "content": "Create operational execution task for: Next step: wait for generated media assets.",
        "summary": "You are executing as: internal worker.",
    }

    safe = asset_viewer._safe_asset(unsafe_asset)
    safe_text = _json_text({"content": safe.get("content"), "summary": safe.get("summary")})
    assert safe["playable"] is True
    assert safe["metadata_only"] is False
    assert safe["preview_ready"] in {True, False}
    for marker in _unsafe_fast_packet_markers():
        assert marker not in safe_text


def test_creative_assets_show_playable_assets_before_job_evidence() -> None:
    old_store = media_jobs.STORE
    old_get_assets = creative_assets.get_persisted_creative_assets
    old_signed_url = asset_viewer._signed_gateway_url

    def fake_get_persisted_creative_assets(limit: int = 50) -> dict:
        return {
            "success": True,
            "asset_count": 4,
            "total_asset_count": 4,
            "assets": [
                {
                    "asset_id": "video_metadata_only_asset",
                    "media_job_id": "media_job_completed_with_audio",
                    "agent_id": "creative_media_agent",
                    "provider": "runway",
                    "asset_type": "video",
                    "status": "completed",
                    "provider_asset_url": "https://example.com/generated/video.mp4",
                    "preview_url": "https://example.com/generated/video.mp4",
                    "download_url": "https://example.com/generated/video.mp4",
                    "playable": True,
                    "preview_ready": True,
                    "download_ready": True,
                    "metadata_only": False,
                    "summary": "Video provider returned placeholder URL.",
                    "credential_values_exposed": False,
                },
                {
                    "asset_id": "localhost_video_asset",
                    "media_job_id": "media_job_completed_with_audio",
                    "agent_id": "creative_media_agent",
                    "provider": "runway",
                    "asset_type": "video",
                    "status": "completed",
                    "provider_asset_url": "http://127.0.0.1:8000/generated/video.mp4",
                    "playable": True,
                    "preview_ready": True,
                    "download_ready": True,
                    "metadata_only": False,
                    "summary": "Video provider returned local URL.",
                    "credential_values_exposed": False,
                },
                {
                    "asset_id": "windows_temp_video_asset",
                    "media_job_id": "media_job_completed_with_audio",
                    "agent_id": "creative_media_agent",
                    "provider": "runway",
                    "asset_type": "video",
                    "status": "completed",
                    "provider_asset_url": "C:\\Users\\User\\AppData\\Local\\Temp\\video.mp4",
                    "playable": True,
                    "preview_ready": True,
                    "download_ready": True,
                    "metadata_only": False,
                    "summary": "Video provider returned temp path.",
                    "credential_values_exposed": False,
                },
                {
                    "asset_id": "audio_playable_asset",
                    "media_job_id": "media_job_completed_with_audio",
                    "agent_id": "creative_media_agent",
                    "provider": "elevenlabs",
                    "asset_type": "audio",
                    "status": "persisted",
                    "playable": True,
                    "preview_ready": True,
                    "download_ready": True,
                    "metadata_only": False,
                    "provider_asset_url": "https://demo.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
                    "preview_url": "https://demo.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
                    "download_url": "https://demo.supabase.co/storage/v1/object/public/creative-media/audio.mp3",
                    "summary": "Playable audio voiceover.",
                    "credential_values_exposed": False,
                },
            ],
            "providers_checked": ["elevenlabs", "runway", "internal"],
            "credential_values_exposed": False,
        }

    with TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        media_jobs.STORE.mkdir(parents=True, exist_ok=True)
        creative_assets.get_persisted_creative_assets = fake_get_persisted_creative_assets
        asset_viewer._signed_gateway_url = lambda asset_id, delivery_type="preview": f"https://signed.example/{delivery_type}/{asset_id}"
        try:
            job = media_jobs.enqueue_media_job(
                task="Create one creative media output packet for a premium skincare serum.",
                agent_id="creative_media_agent",
                tenant_id="client_demo",
                include_audio=True,
                include_video=True,
            )
            job.update(
                {
                    "status": "completed",
                    "worker_claimed": True,
                    "worker_completed": True,
                    "durable_queue_status": "completed",
                    "provider_status": "runway",
                    "media_asset_count": 2,
                    "real_media_asset_count": 2,
                    "persisted_asset_count": 2,
                    "playable_asset_count": 1,
                    "preview_ready_count": 1,
                    "download_ready_count": 1,
                    "signed_delivery_created": True,
                    "final_assets": [
                        {"asset_id": "video_metadata_only_asset", "asset_type": "video", "playable": False, "metadata_only": True},
                        {"asset_id": "audio_playable_asset", "asset_type": "audio", "playable": True, "preview_ready": True, "download_ready": True},
                    ],
                    "final_asset_ids": ["video_metadata_only_asset", "audio_playable_asset"],
                }
            )
            media_jobs._write_job(job)

            result = asset_viewer.get_admin_creative_media_assets(limit=10)
        finally:
            asset_viewer._signed_gateway_url = old_signed_url
            creative_assets.get_persisted_creative_assets = old_get_assets
            media_jobs.STORE = old_store

    assert result["success"] is True
    assert result["playable_asset_count"] == 1
    assert result["evidence_row_count"] == 1
    assert result["metadata_only_count"] >= 4
    assert result["total_detected"] == 5

    assets = result["assets"]
    assert assets[0]["asset_id"] == "audio_playable_asset"
    assert assets[0]["playable"] is True
    assert assets[0]["preview_ready"] is True
    assert assets[0]["download_ready"] is True
    assert assets[1]["asset_id"] == "video_metadata_only_asset"
    assert assets[1]["playable"] is False
    assert assets[1]["metadata_only"] is True
    assert assets[1]["preview_ready"] is False
    assert assets[1]["download_ready"] is False
    assert assets[1]["signed_delivery_created"] is False
    assert assets[1]["delivery_status"] == "blocked_placeholder_source"
    assert assets[1]["not_playable_reason"] == "placeholder_or_invalid_media_source"
    blocked = {asset["asset_id"]: asset for asset in assets if asset.get("asset_id") in {"localhost_video_asset", "windows_temp_video_asset"}}
    assert blocked["localhost_video_asset"]["playable"] is False
    assert blocked["localhost_video_asset"]["not_playable_reason"] == "placeholder_or_invalid_media_source"
    assert blocked["windows_temp_video_asset"]["playable"] is False
    assert blocked["windows_temp_video_asset"]["not_playable_reason"] == "placeholder_or_invalid_media_source"
    evidence = [asset for asset in assets if asset.get("asset_type") == "creative_media_job_evidence"]
    assert evidence
    assert evidence[0]["playable"] is False
    assert evidence[0]["final_combined_asset_ready"] is False
    assert evidence[0]["final_combined_asset_required"] is True
    assert evidence[0]["final_combined_asset_status"] == "pending_composition"
    assert evidence[0]["separate_audio_ready"] is True
    assert evidence[0]["separate_video_ready"] is False


def test_platform_instruction_text_never_becomes_creative_brief_fields() -> None:
    unsafe_task = (
        "This is a unique multi-agent, multi-industry platform. "
        "Do not default to ecommerce unless the task is ecommerce-specific. "
        "Platform standard: internal routing and backend instructions."
    )
    job = {
        "job_id": "media_job_internal_platform_text",
        "status": "completed",
        "task": unsafe_task,
        "include_audio": True,
        "include_video": True,
    }

    safe_job = media_jobs._status_safe_job(job)
    packet = media_jobs.build_fast_creative_output_packet(job)
    combined_text = _json_text({"job": safe_job, "packet": packet})

    assert safe_job["task"] == media_jobs.UNSAFE_CREATIVE_BRIEF_FALLBACK
    assert safe_job["customer_task"] == media_jobs.UNSAFE_CREATIVE_BRIEF_FALLBACK
    assert packet["fast_output_packet_available"] is False
    assert "creative_brief" not in packet
    assert "hook" not in packet
    assert "caption" not in packet
    for marker in _unsafe_fast_packet_markers():
        assert marker not in combined_text


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
    test_durable_queue_claim_sql_qualifies_returning_columns_and_claims_queue()
    test_background_worker_entrypoint_defines_media_processor_before_main_runs()
    test_render_worker_service_enables_media_worker_loop()
    test_worker_claims_durable_media_queue_and_status_overlay_moves_job_out_of_queued()
    test_worker_outcome_remains_visible_without_local_media_job_json()
    test_asset_viewer_sanitises_operational_asset_content_without_changing_playability()
    test_creative_assets_show_playable_assets_before_job_evidence()
    test_platform_instruction_text_never_becomes_creative_brief_fields()
    print("MEDIA_WORKER_BOUNDARY_PASSED")
