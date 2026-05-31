
from backend.app.runtime.global_execution_evidence_layer import build_execution_evidence_packet

admin_packet = build_execution_evidence_packet(
    tenant_id="client_demo_001",
    limit=10,
    actor_role="owner_admin",
)

assert admin_packet["success"] is True
assert admin_packet["admin_view"] is True
assert admin_packet["credential_values_exposed"] is False

client_packet = build_execution_evidence_packet(
    tenant_id="client_demo_001",
    limit=10,
    actor_role="client",
)

assert client_packet["success"] is True
assert client_packet["admin_view"] is False
assert client_packet["credential_values_exposed"] is False

print("GLOBAL_EXECUTION_EVIDENCE_LAYER_TEST_PASSED")
