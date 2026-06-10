import os
from starlette.requests import Request

from backend.app.core import session_auth_hardening_runtime as session_auth


MEDIA_JOB_ROUTES = [
    "/admin/media-jobs/run-next",
    "/admin/media-jobs/run-all",
    "/admin/media-jobs/trigger-next",
    "/admin/media-jobs/trigger-all",
]


def make_request(
    path,
    method="POST",
    token="test-admin-token",
    role="owner_admin",
    tenant="owner_admin",
    include_auth=True,
):
    headers = [
        (b"host", b"testserver"),
        (b"x-actor-role", role.encode("utf-8")),
        (b"x-tenant-id", tenant.encode("utf-8")),
        (b"user-agent", b"media-job-session-hardening-test"),
    ]

    if include_auth:
        headers.append((b"x-admin-token", token.encode("utf-8")))
        headers.append((b"authorization", f"Bearer {token}".encode("utf-8")))

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": headers,
        "query_string": b"",
        "scheme": "https",
        "server": ("testserver", 443),
        "client": ("127.0.0.1", 12345),
    }
    return Request(scope)


def test_media_job_processing_paths_are_governed_execution_paths():
    old_env = os.environ.get("APP_ENV")
    os.environ["APP_ENV"] = "production"

    try:
        for route in MEDIA_JOB_ROUTES:
            assert session_auth._is_governed_execution_path(route) is True

            assessment = session_auth.assess_session_auth_request(make_request(route))
            assert assessment["blocked"] is False, assessment
            assert "csrf_token_or_origin_missing_for_state_change" not in assessment.get("reasons", []), assessment

            missing_auth_request = make_request(route, include_auth=False)
            missing_auth_assessment = session_auth.assess_session_auth_request(missing_auth_request)
            assert missing_auth_assessment["blocked"] is True, missing_auth_assessment
            assert "production_admin_missing_authorization" in missing_auth_assessment.get("reasons", []), missing_auth_assessment

            bad_role_assessment = session_auth.assess_session_auth_request(make_request(route, role="client"))
            assert bad_role_assessment["blocked"] is True, bad_role_assessment

    finally:
        if old_env is None:
            os.environ.pop("APP_ENV", None)
        else:
            os.environ["APP_ENV"] = old_env


if __name__ == "__main__":
    test_media_job_processing_paths_are_governed_execution_paths()
    print("MEDIA_JOB_SESSION_HARDENING_GOVERNED_PATHS_TEST_PASSED")
