
from pathlib import Path

main = Path("backend/app/main.py").read_text(encoding="utf-8")

assert "build_global_connector_execution_packet" in main
assert '"global_provider_connector"' in main
assert "global_real_provider_connector_layer" in main

print("GLOBAL_CONNECTOR_RUN_AGENT_WIRING_OK")
