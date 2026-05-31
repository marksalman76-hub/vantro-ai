
from pathlib import Path

p = Path("backend/app/runtime/real_external_integration_execution_bridge.py")
text = p.read_text(encoding="utf-8")

assert "execute_integration_action" in text
assert 'integration_key="email"' in text
assert 'action="send_email"' in text
assert "email_sent" in text
assert "email_live_execution_failed" in text
assert "credential_exposed" in text

print("BREVO_LIVE_EMAIL_BRIDGE_WIRING_TEST_PASSED")
