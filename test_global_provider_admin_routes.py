
from pathlib import Path

main = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "/admin/global-provider/readiness" in main
assert "/admin/global-provider/execution-packet" in main
assert "real_provider_activation_readiness" in main
assert "global_provider_execution_readiness" in main
assert "global_real_provider_connector_readiness" in main

print("GLOBAL_PROVIDER_ADMIN_ROUTES_OK")
