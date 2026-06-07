from pathlib import Path


ROOT = Path.cwd()


def read(path: str) -> str:
    target = ROOT / path
    if not target.exists():
        raise AssertionError(f"Missing required file: {path}")
    return target.read_text(encoding="utf-8")


def assert_contains(path: str, needles: list[str]) -> None:
    text = read(path)
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise AssertionError(f"{path} missing {missing}")


def assert_order(path: str, first: str, second: str) -> None:
    text = read(path)
    first_index = text.find(first)
    second_index = text.find(second)
    if first_index < 0 or second_index < 0 or first_index > second_index:
        raise AssertionError(f"{path} expected {first!r} before {second!r}")


def test_backend_canonical_routes_exist() -> None:
    assert_contains(
        "backend/app/main.py",
        [
            '@app.get("/client-business-profile")',
            '@app.post("/client-business-profile")',
            '@app.post("/client-review-action")',
            '@app.get("/client-review-action")',
            '@app.post("/client-execution-state")',
            '@app.get("/client-execution-state")',
            "record_approval_action_audit",
            "record_execution_evidence",
            '"authority": "backend_canonical"',
            '"credential_values_exposed": False',
        ],
    )


def test_business_profile_backend_first_and_advisory_fallback() -> None:
    path = "frontend/src/app/api/client-business-profile/route.ts"
    assert_contains(
        path,
        [
            "safeBackendProfile",
            "advisoryProfileResponse",
            "productionFailClosed",
            'authority: "backend_canonical"',
            'authority: "frontend_advisory"',
            "production_fail_closed: true",
            "credential_values_exposed: false",
        ],
    )
    assert_order(path, "const { status, payload } = await readBackendProfile(req);", "return advisoryProfileResponse(tenantKey")


def test_review_action_backend_first_and_production_fail_closed() -> None:
    path = "frontend/src/app/api/client-review-action/route.ts"
    assert_contains(
        path,
        [
            'fetch(`${backendBaseUrl()}/client-review-action`',
            "persistApprovalRevisionEvent",
            'authority: "backend_canonical"',
            'authority: "frontend_advisory"',
            "productionFailClosed",
            "production_fail_closed: true",
            "credential_values_exposed: false",
        ],
    )
    assert_order(path, 'fetch(`${backendBaseUrl()}/client-review-action`', "persistApprovalRevisionEvent(tenantKey")


def test_execution_state_backend_canonical_or_advisory() -> None:
    assert_contains(
        "frontend/src/app/api/delegated-workforce-execution/route.ts",
        [
            "syncBackendCanonicalExecutionState",
            'fetch(`${backendBaseUrl()}/client-execution-state`',
            'normalised.execution_state_authority = "backend_canonical"',
            'normalised.execution_state_authority = "frontend_advisory"',
            "normalised.execution_state_production_fail_closed = true",
            "credential_values_exposed: false",
        ],
    )
    assert_contains(
        "frontend/src/lib/executionStateSync.ts",
        [
            'authority?: "backend_canonical" | "frontend_advisory"',
            "fallback_used?: boolean",
            "dev_only?: boolean",
            "production_fail_closed?: boolean",
            "credential_values_exposed?: false",
        ],
    )


def test_integration_state_fails_closed_without_credential_exposure() -> None:
    assert_contains(
        "backend/app/core/client_integrations_runtime.py",
        [
            "def _production_fail_closed",
            '"production_fail_closed": True',
            '"credential_values_exposed": False',
            "elif _is_production():",
            "canonical_integration_store_unavailable",
        ],
    )


if __name__ == "__main__":
    test_backend_canonical_routes_exist()
    test_business_profile_backend_first_and_advisory_fallback()
    test_review_action_backend_first_and_production_fail_closed()
    test_execution_state_backend_canonical_or_advisory()
    test_integration_state_fails_closed_without_credential_exposure()
    print("TASK_10C_A_CUSTOMER_STATE_AUTHORITY_PASSED")
