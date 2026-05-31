from backend.app.core.rate_shaping_middleware import (
    rate_shaping_middleware_default_mode,
    rate_shaping_middleware_changes_live_runtime,
    rate_shaping_middleware_blocks_by_default,
)
from pathlib import Path


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    main_file = Path("backend/app/main.py")
    text = main_file.read_text(encoding="utf-8", errors="replace")

    if "RateShapingMiddleware" not in text:
        raise AssertionError("RateShapingMiddleware not wired in backend/app/main.py")

    assert_equal(rate_shaping_middleware_default_mode(), "observe", "default mode")
    assert_equal(rate_shaping_middleware_changes_live_runtime(), True, "middleware wired")
    assert_equal(rate_shaping_middleware_blocks_by_default(), False, "does not block by default")

    print("RATE_SHAPING_MIDDLEWARE_WIRING_TEST_PASSED")


if __name__ == "__main__":
    main()
