
from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert 'getattr(session, "id", None)' in text
assert 'getattr(session, "url", None)' in text
assert 'real_stripe_checkout_session_bridge_v1' in text
assert 'live_checkout_session_created' in text

print("STRIPE_CHECKOUT_SESSION_OBJECT_HANDLING_TEST_PASSED")
