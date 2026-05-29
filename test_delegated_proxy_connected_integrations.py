
from pathlib import Path

p = Path("frontend/src/app/api/delegated-workforce-execution/route.ts")
text = p.read_text(encoding="utf-8")

assert "connected_integrations: body.connected_integrations || []" in text
assert "package_tier: body.package_tier ||" in text

print("DELEGATED_PROXY_CONNECTED_INTEGRATIONS_TEST_PASSED")
