from pathlib import Path

def main():
    text = Path("backend/app/main.py").read_text(encoding="utf-8", errors="replace")
    required = [
        "/admin/live-provider-readiness",
        "openai_configured",
        "owner_approved_live_activation",
        "provider_execution_ready",
        "secret_values_exposed",
        "LIVE_PROVIDER_READY",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise AssertionError(f"Missing provider readiness route markers: {missing}")
    print("LIVE_PROVIDER_READINESS_ROUTE_TEST_PASSED")

if __name__ == "__main__":
    main()
