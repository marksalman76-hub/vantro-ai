import os
from starlette.requests import Request

from backend.app.runtime.ai_media_session_auth_compat import validate_ai_media_admin_session_compatibility


MEDIA_JOB_ROUTES = [
    "/admin/media-jobs/run-next",
    "/admin/media-jobs/run-all",
    "/admin/media-jobs/trigger-next",
    "/admin/media-jobs/trigger-all",
]


def make_request(path, method="POST", token="test-admin-token", role="owner_admin"):
    headers = [
        (b"host", b"testserver"),
        (b"x-actor-role", role.encode("utf-8")),
        (b"x-admin-token", token.encode("utf-8")),
        (b"authorization", f"Bearer {token}".encode("utf-8")),
    ]
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


def test_media_job_session_auth_compat_allowlist():
    old_token = os.environ.get("ADMIN_PLATFORM_TOKEN")
    os.environ["ADMIN_PLATFORM_TOKEN"] = "test-admin-token"

    try:
        for route in MEDIA_JOB_ROUTES:
            allowed = validate_ai_media_admin_session_compatibility(make_request(route))
            assert allowed["allowed"] is True, allowed

            bad_role = validate_ai_media_admin_session_compatibility(make_request(route, role="client"))
            assert bad_role["allowed"] is False, bad_role

            bad_token = validate_ai_media_admin_session_compatibility(make_request(route, token="bad-token"))
            assert bad_token["allowed"] is False, bad_token

            bad_method = validate_ai_media_admin_session_compatibility(make_request(route, method="GET"))
            assert bad_method["allowed"] is False, bad_method

    finally:
        if old_token is None:
            os.environ.pop("ADMIN_PLATFORM_TOKEN", None)
        else:
            os.environ["ADMIN_PLATFORM_TOKEN"] = old_token


if __name__ == "__main__":
    test_media_job_session_auth_compat_allowlist()
    print("MEDIA_JOB_SESSION_AUTH_COMPAT_ALLOWLIST_TEST_PASSED")
