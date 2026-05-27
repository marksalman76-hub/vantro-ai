from pathlib import Path

files = [
    Path("backend/app/core/production_security_switch.py"),
    Path("backend/app/core/security_audit_enforcement_runtime.py"),
    Path("backend/app/core/priority5_final_security_readiness.py"),
    Path("backend/app/core/saas_provisioning_runtime.py"),
    Path("backend/app/core/integration_live_adapter_registry.py"),
    Path("backend/app/runtime/provider_connector_registry.py"),
]

terms = [
    "invalid_token",
    "ADMIN_PLATFORM_TOKEN",
    "ADMIN_AUTH_SECRET",
    "Authorization",
    "bearer",
    "Bearer",
]

for file in files:
    if not file.exists():
        continue

    lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()

    print("\n" + "=" * 80)
    print(file)
    print("=" * 80)

    for i, line in enumerate(lines):
        if any(term in line for term in terms):
            start = max(0, i - 8)
            end = min(len(lines), i + 12)

            print(f"\n--- around line {i + 1} ---")
            for n in range(start, end):
                safe_line = lines[n]
                print(f"{n + 1}: {safe_line}")