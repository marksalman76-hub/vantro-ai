import os
from starlette.requests import Request

from backend.app.core import security_audit_enforcement_runtime as security


def make_request(path, method="GET", token="test-admin-token", role="owner_admin"):
    headers = [
        (b"host", b"testserver"),
        (b"x-actor-role", role.encode("utf-8")),
        (b"x-admin-token", token.encode("utf-8")),
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


def test_media_job_diagnostics_security_allowlist():
    old_token = os.environ.get("ADMIN_PLATFORM_TOKEN")
    os.environ["ADMIN_PLATFORM_TOKEN"] = "test-admin-token"

    try:
        assert security._admin_media_job_processing_valid(
            make_request("/admin/security/media-job-read-diagnostics")
        ) is True

        assert security._admin_media_job_processing_valid(
            make_request("/admin/security/media-job-read-diagnostics", token="bad-token")
        ) is False

        assert security._admin_media_job_processing_valid(
            make_request("/admin/security/media-job-read-diagnostics", role="client")
        ) is False

        assert security._admin_media_job_processing_valid(
            make_request("/admin/security/media-job-read-diagnostics", method="POST")
        ) is False

    finally:
        if old_token is None:
            os.environ.pop("ADMIN_PLATFORM_TOKEN", None)
        else:
            os.environ["ADMIN_PLATFORM_TOKEN"] = old_token


if __name__ == "__main__":
    test_media_job_diagnostics_security_allowlist()
    print("MEDIA_JOB_DIAGNOSTICS_SECURITY_ALLOWLIST_TEST_PASSED")
