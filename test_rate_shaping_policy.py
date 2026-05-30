from backend.app.core.rate_shaping_policy import (
    classify_route,
    get_policy_for_path,
    should_owner_admin_bypass,
    export_rate_policy_snapshot,
)


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    cases = {
        "/health": "health",
        "/admin/provider-execution/summary": "provider_execution",
        "/admin/security-hardening-readiness": "readiness",
        "/api/client-login": "auth",
        "/api/run-agent": "client_execution",
        "/api/delegated-workforce-execution": "client_execution",
        "/api/public-demo": "public",
    }

    for path, expected in cases.items():
        assert_equal(classify_route(path), expected, path)

    assert_equal(should_owner_admin_bypass("/admin/provider-execution/summary"), True, "provider admin bypass")
    assert_equal(should_owner_admin_bypass("/api/run-agent"), False, "client execution no bypass")
    assert_equal(should_owner_admin_bypass("/health"), False, "health no bypass")

    health = get_policy_for_path("/health")
    if health.limit_per_minute < 100:
        raise AssertionError("health limit too low for production probes")

    snapshot = export_rate_policy_snapshot()
    required = ["health", "readiness", "client_execution", "admin_execution", "provider_execution", "auth", "public"]
    missing = [key for key in required if key not in snapshot]
    if missing:
        raise AssertionError(f"Missing policies: {missing}")

    print("RATE_SHAPING_POLICY_TEST_PASSED")
    print("Policy groups:", ", ".join(sorted(snapshot.keys())))


if __name__ == "__main__":
    main()
