import os

from backend.app.main import admin_media_job_read_diagnostics


def test_media_job_read_diagnostics_route():
    old_token = os.environ.get("ADMIN_PLATFORM_TOKEN")
    os.environ["ADMIN_PLATFORM_TOKEN"] = "diagnostic-token"

    try:
        ok = admin_media_job_read_diagnostics(
            request=None,
            path="/admin/media-jobs/media_job_test_123",
            x_actor_role="owner_admin",
            x_admin_token="diagnostic-token",
            authorization=None,
        )

        assert ok["success"] is True
        assert ok["token_valid"] is True
        assert ok["role_allowed"] is True
        assert ok["media_job_read_prefix_allowed"] is True
        assert ok["media_job_read_allowed"] is True
        assert ok["credential_values_exposed"] is False
        assert ok["token_value_exposed"] is False
        assert ok["raw_provider_payload_exposed"] is False
        assert ok["internal_prompt_exposed"] is False

        bad_token = admin_media_job_read_diagnostics(
            request=None,
            path="/admin/media-jobs/media_job_test_123",
            x_actor_role="owner_admin",
            x_admin_token="bad-token",
            authorization=None,
        )

        assert bad_token["token_valid"] is False
        assert bad_token["media_job_read_allowed"] is False

        bad_role = admin_media_job_read_diagnostics(
            request=None,
            path="/admin/media-jobs/media_job_test_123",
            x_actor_role="client",
            x_admin_token="diagnostic-token",
            authorization=None,
        )

        assert bad_role["role_allowed"] is False
        assert bad_role["media_job_read_allowed"] is False

    finally:
        if old_token is None:
            os.environ.pop("ADMIN_PLATFORM_TOKEN", None)
        else:
            os.environ["ADMIN_PLATFORM_TOKEN"] = old_token


if __name__ == "__main__":
    test_media_job_read_diagnostics_route()
    print("MEDIA_JOB_READ_DIAGNOSTICS_ROUTE_TEST_PASSED")