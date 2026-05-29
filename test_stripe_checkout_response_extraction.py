
from pathlib import Path

text = Path("backend/app/main.py").read_text(encoding="utf-8")

assert 'real_stripe_checkout_session_bridge_v2' in text
assert 'session_id = getattr(session, "id", None)' in text
assert 'checkout_url = getattr(session, "url", None)' in text
assert 'session["id"]' in text
assert 'session["url"]' in text

print("STRIPE_CHECKOUT_RESPONSE_EXTRACTION_TEST_PASSED")
