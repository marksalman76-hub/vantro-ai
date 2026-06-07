from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any, Dict, Iterator

from starlette.responses import JSONResponse

from backend.app.core.security_audit_enforcement_runtime import assess_audit_enforcement
from backend.app.runtime import async_media_job_foundation as media_jobs
from backend.app.runtime import creative_asset_persistence_bridge as creative_assets
from backend.app.runtime import shared_creative_media_generation_runtime as shared_media
from backend.app.runtime.admin_creative_media_asset_viewer import get_admin_creative_media_assets
from backend.app import main as backend_main


class HeaderMap(dict):
    def get(self, key: str, default: str = "") -> str:
        return super().get(key.lower(), default)


def fake_request(path: str, *, method: str = "POST", headers: Dict[str, str] | None = None) -> Any:
    return SimpleNamespace(
        url=SimpleNamespace(path=path),
        method=method,
        headers=HeaderMap({str(k).lower(): str(v) for k, v in (headers or {}).items()}),
        client=SimpleNamespace(host="127.0.0.1"),
    )


def contains_unsafe(value: object) -> bool:
    text = json.dumps(value, sort_keys=True).lower()
    return any(
        marker in text
        for marker in [
            "super_secret_provider_token",
            "raw_provider_payload",
            "debug_trace",
            "internal_prompt",
        ]
    )


@contextmanager
def production_admin_env() -> Iterator[None]:
    original = {key: os.environ.get(key) for key in ["APP_ENV", "ADMIN_PLATFORM_TOKEN"]}
    os.environ["APP_ENV"] = "production"
    os.environ["ADMIN_PLATFORM_TOKEN"] = "test-admin-token"
    try:
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@contextmanager
def provider_unavailable_media_generation() -> Iterator[None]:
    original = shared_media.generate_creative_media_pack

    def fake_generate_creative_media_pack(**kwargs: Any) -> Dict[str, Any]:
        return {
            "success": True,
            "media_pack_id": "media_pack_provider_unavailable",
            "media_assets": [],
            "real_media_asset_count": 0,
            "persisted_asset_count": 0,
            "playable_asset_count": 0,
            "provider_execution_results": [
                {
                    "status": "prepared_no_live_provider_configured",
                    "raw_provider_payload": "raw_provider_payload",
                    "credential_values_exposed": False,
                }
            ],
            "generation_jobs": [
                {
                    "status": "prepared_no_live_provider_configured",
                    "live_generation_available": False,
                    "live_provider_execution_attempted": False,
                }
            ],
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    shared_media.generate_creative_media_pack = fake_generate_creative_media_pack
    try:
        yield
    finally:
        shared_media.generate_creative_media_pack = original


def test_admin_media_job_processing_security_path() -> None:
    old_store = media_jobs.STORE
    with production_admin_env(), TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        media_jobs.STORE.mkdir(parents=True, exist_ok=True)
        try:
            unauthorised_assessment = assess_audit_enforcement(
                fake_request("/admin/media-jobs/run-all", headers={"x-actor-role": "owner_admin"})
            )
            assert unauthorised_assessment["blocked"] is True
            assert "admin_token_missing_or_invalid" in unauthorised_assessment["reasons"]

            authorised_assessment = assess_audit_enforcement(
                fake_request(
                    "/admin/media-jobs/run-all",
                    headers={
                        "x-actor-role": "owner_admin",
                        "x-admin-token": "test-admin-token",
                    },
                )
            )
            assert authorised_assessment["blocked"] is False
            assert authorised_assessment["suspicious"] is False

            blocked_response = backend_main.admin_run_all_media_jobs(
                x_admin_token=None,
                x_actor_role="owner_admin",
                authorization=None,
            )
            assert isinstance(blocked_response, JSONResponse)
            assert blocked_response.status_code == 403

            job = media_jobs.enqueue_media_job(
                task="Create governed creative media.",
                agent_id="ugc_creative_agent",
                tenant_id="client_demo_001",
                include_image=True,
                include_audio=True,
                include_video=True,
            )
            job["provider_token"] = "super_secret_provider_token"
            job["debug_trace"] = {"raw_provider_payload": "raw_provider_payload"}
            job["internal_prompt"] = "internal_prompt"
            media_jobs._write_job(job)

            with provider_unavailable_media_generation():
                result = backend_main.admin_run_all_media_jobs(
                    x_admin_token="test-admin-token",
                    x_actor_role="owner_admin",
                    authorization=None,
                )

            assert isinstance(result, dict)
            assert result["success"] is True
            assert result["authorised"] is True
            assert result["processor_invoked"] is True
            assert result["processed_job_count"] == 1
            assert result["final_status_counts"].get("provider_unavailable") == 1
            assert result["security_profile"] == "priority5_security_audit_enforcement_v1"
            assert result["credential_values_exposed"] is False
            assert not contains_unsafe(result)

            processed_job = media_jobs.read_media_job(job["job_id"])
            assert processed_job["status"] == "provider_unavailable"
            assert processed_job["status"] != "queued"

            admin_assets = get_admin_creative_media_assets(limit=10)
            evidence = [asset for asset in admin_assets["assets"] if asset.get("asset_id") == job["job_id"]]
            assert evidence
            assert evidence[0]["status"] == "provider_unavailable"
            assert evidence[0]["credential_values_exposed"] is False
            assert not contains_unsafe(admin_assets)
        finally:
            media_jobs.STORE = old_store


def test_admin_run_delegated_workforce_click_chain_is_observable() -> None:
    admin_page = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

    handler_start = admin_page.index("async function runDelegatedWorkforcePlan()")
    handler_end = admin_page.index("const navItems", handler_start)
    handler = admin_page[handler_start:handler_end]

    delegated_call = handler.index('fetch("/api/delegated-workforce-execution"')
    media_call = handler.index('fetch("/api/admin-media-jobs-run-all"')
    assert delegated_call < media_call
    assert "const mediaJobsResponse = await fetch" in handler
    assert "const mediaJobsResult = await mediaJobsResponse.json()" in handler
    assert "setLatestMediaProcessorResult(mediaProcessorSnapshot)" in handler
    assert "mediaProcessorSnapshot.error" in handler
    assert "media_processor_called: true" in handler
    assert "processor_invoked" in handler
    assert "processed_job_count" in handler
    assert "final_status_counts" in handler

    rendered_fields = [
        "Delegated workforce",
        "Media processor",
        "Authorisation",
        "Final statuses",
        "Processor error",
    ]
    for field in rendered_fields:
        assert field in admin_page

    run_all_route = Path("frontend/src/app/api/admin-media-jobs-run-all/route.ts").read_text(encoding="utf-8")
    assert "adminPortalAuthorised(req)" in run_all_route
    assert 'req.cookies.get("portal_access")' in run_all_route
    assert 'req.cookies.get("admin_session")' in run_all_route
    assert "ADMIN_AUTH_SECRET" in run_all_route
    assert '"x-admin-token"' in run_all_route
    assert "admin_authorisation_required" in run_all_route
    assert "auth_sources_checked" in run_all_route
    assert "cookies_present" in run_all_route
    assert "missing_expected_admin_session_cookie" in run_all_route


def test_admin_login_session_cookie_matches_media_runner_auth_sources() -> None:
    login_route = Path("frontend/src/app/api/login/route.ts").read_text(encoding="utf-8")
    admin_login_route = Path("frontend/src/app/api/admin-login/route.ts").read_text(encoding="utf-8")
    logout_route = Path("frontend/src/app/api/logout/route.ts").read_text(encoding="utf-8")
    admin_logout_route = Path("frontend/src/app/api/admin-logout/route.ts").read_text(encoding="utf-8")
    run_all_route = Path("frontend/src/app/api/admin-media-jobs-run-all/route.ts").read_text(encoding="utf-8")
    run_next_route = Path("frontend/src/app/api/admin-media-jobs-run-next/route.ts").read_text(encoding="utf-8")
    delegated_route = Path("frontend/src/app/api/delegated-workforce-execution/route.ts").read_text(encoding="utf-8")

    for route_text in [login_route, admin_login_route]:
        assert 'cookies.set("portal_access"' in route_text
        assert 'cookies.set("admin_session"' in route_text
        assert "PORTAL_ACCESS_CODE" in route_text

    for route_text in [logout_route, admin_logout_route]:
        assert 'cookies.set("portal_access", ""' in route_text
        assert 'cookies.set("admin_session", ""' in route_text

    for route_text in [run_all_route, run_next_route, delegated_route]:
        assert 'req.cookies.get("portal_access")' in route_text
        assert 'req.cookies.get("admin_session")' in route_text
        assert "expectedPortalAccess && portalAccess === expectedPortalAccess" in route_text
        assert "expectedPortalAccess && adminSession === expectedPortalAccess" in route_text

    for route_text in [run_all_route, run_next_route]:
        assert "cookie:portal_access" in route_text
        assert "cookie:admin_session" in route_text
        assert "header:x-admin-token" in route_text
        assert "header:authorization" in route_text
        assert "cookies_present" in route_text
        assert ".value" not in route_text.split("cookies_present", 1)[1].split("reason", 1)[0]


def test_visible_creative_asset_queue_reconciles_to_processor_store() -> None:
    old_store = media_jobs.STORE
    old_get_persisted = creative_assets.get_persisted_creative_assets

    visible_job_id = "media_job_visible_queue_001"

    def fake_get_persisted_creative_assets(limit: int = 100) -> Dict[str, Any]:
        return {
            "success": True,
            "asset_count": 1,
            "total_asset_count": 1,
            "assets": [
                {
                    "asset_id": visible_job_id,
                    "media_job_id": visible_job_id,
                    "tenant_id": "client_demo_001",
                    "agent_id": "ugc_creative_agent",
                    "provider": "creative_media_queue",
                    "provider_key": "creative_media_queue",
                    "asset_type": "creative_media_job_evidence",
                    "media_type": "creative_media_job_evidence",
                    "title": "Creative media job queued",
                    "status": "queued",
                    "summary": "Existing visible queued creative media evidence.",
                    "preview_ready": False,
                    "download_ready": False,
                    "playable": False,
                    "metadata_only": True,
                    "credential_values_exposed": False,
                }
            ],
            "providers_checked": ["elevenlabs", "runway", "heygen", "kling", "sync", "internal"],
            "credential_values_exposed": False,
        }

    with production_admin_env(), TemporaryDirectory() as temp_dir:
        media_jobs.STORE = Path(temp_dir)
        media_jobs.STORE.mkdir(parents=True, exist_ok=True)
        creative_assets.get_persisted_creative_assets = fake_get_persisted_creative_assets
        try:
            assert not (media_jobs.STORE / f"{visible_job_id}.json").exists()

            admin_assets_before = get_admin_creative_media_assets(limit=10)
            visible_before = [
                asset for asset in admin_assets_before["assets"] if asset.get("asset_id") == visible_job_id
            ]
            assert visible_before
            assert visible_before[0]["status"] == "queued"
            assert admin_assets_before["canonical_store"] == "backend:runtime_outputs/media_jobs"
            assert admin_assets_before["store_paths_match"] is True

            media_jobs_before = backend_main.admin_list_media_jobs(x_actor_role="owner_admin")
            listed_before = [
                job for job in media_jobs_before["jobs"] if job.get("job_id") == visible_job_id
            ]
            assert listed_before
            assert listed_before[0]["status"] == "queued"
            assert media_jobs_before["queued_job_count"] == 1
            assert (media_jobs.STORE / f"{visible_job_id}.json").exists()

            with provider_unavailable_media_generation():
                result = backend_main.admin_run_all_media_jobs(
                    x_admin_token="test-admin-token",
                    x_actor_role="owner_admin",
                    authorization=None,
                )

            assert result["success"] is True
            assert result["authorised"] is True
            assert result["processor_invoked"] is True
            assert result["canonical_store"] == "backend:runtime_outputs/media_jobs"
            assert result["visible_queued_job_count_before"] == 1
            assert result["processor_queued_job_count_before"] == 1
            assert result["processed_job_count"] == 1
            assert result["store_paths_match"] is True
            assert result["final_status_counts"].get("provider_unavailable") == 1
            assert result["credential_values_exposed"] is False
            assert not contains_unsafe(result)

            media_jobs_after = backend_main.admin_list_media_jobs(x_actor_role="owner_admin")
            assert media_jobs_after["queued_job_count"] == 0
            assert media_jobs_after["status_counts"].get("provider_unavailable") == 1

            admin_assets_after = get_admin_creative_media_assets(limit=10)
            visible_after = [
                asset for asset in admin_assets_after["assets"] if asset.get("asset_id") == visible_job_id
            ]
            assert visible_after
            assert visible_after[0]["status"] == "provider_unavailable"
            assert visible_after[0]["status"] != "queued"
            assert admin_assets_after["processor_queued_job_count"] == 0
            assert admin_assets_after["credential_values_exposed"] is False
            assert not contains_unsafe(admin_assets_after)
        finally:
            creative_assets.get_persisted_creative_assets = old_get_persisted
            media_jobs.STORE = old_store


def test_frontend_media_routes_use_canonical_backend_resolver() -> None:
    route_paths = [
        Path("frontend/src/app/api/admin-creative-media-assets/route.ts"),
        Path("frontend/src/app/api/admin-media-jobs/route.ts"),
        Path("frontend/src/app/api/admin-media-jobs-run-all/route.ts"),
        Path("frontend/src/app/api/admin-media-jobs-run-next/route.ts"),
    ]

    for route_path in route_paths:
        route_text = route_path.read_text(encoding="utf-8")
        assert "function backendBaseUrl()" in route_text
        assert "process.env.BACKEND_API_URL" in route_text
        assert "process.env.BACKEND_BASE_URL" in route_text
        assert "process.env.NEXT_PUBLIC_BACKEND_API_URL" in route_text
        assert "process.env.NEXT_PUBLIC_API_BASE_URL" in route_text
        assert "process.env.NEXT_PUBLIC_BACKEND_BASE_URL" in route_text
        assert "https://api.trance-formation.com.au" in route_text

    run_all_route = route_paths[2].read_text(encoding="utf-8")
    assert "/admin/media-jobs" in run_all_route
    assert "visible_queued_job_count_before" in run_all_route
    assert "processor_queued_job_count_before" in run_all_route
    assert "frontend_proxy/backend_processor" in run_all_route


def test_admin_background_noise_cleanup_routes_are_scoped() -> None:
    admin_page = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

    for orphaned_path in [
        "/admin/workflow-provider-routing/readiness",
        "/admin/workflow-provider-routing/list?limit=10",
        "/admin/live-provider-execution/readiness",
        "/admin/live-provider-execution/list?limit=10",
    ]:
        assert orphaned_path not in admin_page

    assert "/admin/dead-letter/list?limit=10" in admin_page
    assert "/admin/manual-review/list?limit=10" in admin_page
    assert 'fetch("/api/admin-runtime"' in admin_page
    assert 'credentials: "include"' in admin_page
    assert 'fetch("/api/admin-media-jobs-run-all"' in admin_page
    assert "mediaProcessorSnapshot.error" in admin_page

    proxy_routes = [
        Path("frontend/src/app/api/admin-billing-refund-requests/route.ts"),
        Path("frontend/src/app/api/admin-industry-agent-store-packs/route.ts"),
        Path("frontend/src/app/api/admin-learning-vault-records/route.ts"),
        Path("frontend/src/app/api/admin-billing-refund-decision/route.ts"),
        Path("frontend/src/app/api/admin-billing-refund-execute/route.ts"),
        Path("frontend/src/app/api/admin-learning-vault-capture/route.ts"),
    ]

    for route_path in proxy_routes:
        route_text = route_path.read_text(encoding="utf-8")
        assert "function serverAdminToken()" in route_text
        assert "process.env.ADMIN_TOKEN" in route_text
        assert "process.env.ADMIN_PLATFORM_TOKEN" in route_text
        assert "process.env.ADMIN_AUTH_SECRET" in route_text
        assert "process.env.OWNER_ADMIN_TOKEN" in route_text
        assert 'req.headers.get("x-admin-token") || serverAdminToken()' in route_text
        assert "`Bearer ${adminToken}`" in route_text


if __name__ == "__main__":
    test_admin_media_job_processing_security_path()
    test_admin_run_delegated_workforce_click_chain_is_observable()
    test_admin_login_session_cookie_matches_media_runner_auth_sources()
    test_visible_creative_asset_queue_reconciles_to_processor_store()
    test_frontend_media_routes_use_canonical_backend_resolver()
    test_admin_background_noise_cleanup_routes_are_scoped()
    print("ADMIN_MEDIA_JOB_SECURITY_PROCESSING_PASSED")
    sys.stdout.flush()
    os._exit(0)
