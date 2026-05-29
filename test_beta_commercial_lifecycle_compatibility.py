
from pathlib import Path

billing = Path("frontend/src/app/api/billing-checkout/route.ts").read_text(encoding="utf-8")
activation = Path("frontend/src/app/api/signup-agent-selection/activation-packet/route.ts").read_text(encoding="utf-8")

assert 'action: body.action || "create_checkout_session"' in billing
assert 'beta_checkout_ready' in billing
assert 'unsupported_billing_action' in billing
assert 'credential_values_exposed: false' in billing

assert 'signup_activation_packet_beta_compatibility_v1' in activation
assert 'PACKAGE_LIMITS' in activation
assert 'ENTERPRISE_ONLY' in activation
assert 'fallback_mode: "frontend_beta_activation_packet"' in activation
assert 'credential_values_exposed: false' in activation

print("BETA_COMMERCIAL_LIFECYCLE_COMPATIBILITY_TEST_PASSED")
