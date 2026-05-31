from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
target = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"

backup_dir = ROOT / "backups" / f"provider_aware_adapter_routing_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / target.name)

text = target.read_text(encoding="utf-8")

old = '''def classify_action_adapter(packet: Dict[str, Any]) -> str:
    text = _text(packet)

    if any(x in text for x in ["stakeholder interview", "interviews", "interview healthcare", "schedule interview"]):
        return "stakeholder_interview_outreach_adapter"

    if any(x in text for x in ["competitor", "white space", "positioning analysis", "landscape analysis"]):
        return "competitor_research_adapter"

    if any(x in text for x in ["thought leadership", "white paper", "whitepaper", "webinar", "blog", "case study"]):
        return "content_asset_creation_adapter"

    if any(x in text for x in ["messaging pillars", "positioning framework", "value proposition", "sales deck"]):
        return "sales_enablement_asset_adapter"

    if any(x in text for x in ["crm", "pipeline", "lead", "prospect", "appointment"]):
        return "crm_task_creation_adapter"

    if any(x in text for x in ["launch campaign", "paid campaign", "increase budget", "ad budget", "go live"]):
        return "approval_gated_campaign_adapter"

    if any(x in text for x in ["send email", "outreach email", "bulk", "mass email"]):
        return "approval_gated_communication_adapter"

    return "general_operational_task_adapter"
'''

new = '''def classify_action_adapter(packet: Dict[str, Any]) -> str:
    text = _text(packet)
    connected = set(packet.get("connected_integrations") or [])

    email_intent = any(x in text for x in [
        "email",
        "brevo",
        "send message",
        "send verification",
        "connected email provider",
        "email provider",
        "outreach message",
        "reply",
        "follow up",
        "follow-up",
    ])

    crm_intent = any(x in text for x in [
        "crm",
        "pipeline",
        "lead",
        "prospect",
        "contact",
        "deal",
        "opportunity",
        "follow-up task",
        "follow up task",
    ])

    calendar_intent = any(x in text for x in [
        "calendar",
        "meeting",
        "appointment",
        "interview slot",
        "book",
        "schedule",
    ])

    stakeholder_intent = any(x in text for x in [
        "stakeholder interview",
        "stakeholder interviews",
        "interviews",
        "interview healthcare",
        "schedule interview",
        "client interview",
        "market validation interview",
        "pilot client",
    ])

    if email_intent and "email" in connected:
        return "stakeholder_interview_outreach_adapter"

    if stakeholder_intent:
        return "stakeholder_interview_outreach_adapter"

    if crm_intent and "crm" in connected:
        return "stakeholder_interview_outreach_adapter"

    if calendar_intent and "calendar" in connected:
        return "stakeholder_interview_outreach_adapter"

    if any(x in text for x in ["competitor", "white space", "positioning analysis", "landscape analysis"]):
        return "competitor_research_adapter"

    if any(x in text for x in ["thought leadership", "white paper", "whitepaper", "webinar", "blog", "case study"]):
        return "content_asset_creation_adapter"

    if any(x in text for x in ["messaging pillars", "positioning framework", "value proposition", "sales deck"]):
        return "sales_enablement_asset_adapter"

    if crm_intent:
        return "crm_task_creation_adapter"

    if any(x in text for x in ["launch campaign", "paid campaign", "increase budget", "ad budget", "go live"]):
        return "approval_gated_campaign_adapter"

    if email_intent:
        return "stakeholder_interview_outreach_adapter"

    return "general_operational_task_adapter"
'''

if old not in text:
    raise SystemExit("CLASSIFIER_BLOCK_NOT_FOUND")

text = text.replace(old, new, 1)

old_call = '''        real_external_result = execute_real_external_action(
            adapter=adapter,
            action_text=str(action_text),
            tenant_id=tenant_id,
            connected_integrations=connected_integrations or [],
            owner_approved=owner_approved,
        )
'''

new_call = '''        real_external_result = execute_real_external_action(
            adapter=adapter,
            action_text=str(action_text),
            tenant_id=tenant_id,
            connected_integrations=connected_integrations or [],
            owner_approved=owner_approved,
        )
'''

# Keep call unchanged; test confirms connected integrations are included in packet classifier path.
text = text.replace(old_call, new_call, 1)

old_adapter_assignment = '''    adapter = (
        packet.get("execution_adapter_target")
        or packet.get("adapter")
        or classify_action_adapter(packet)
    )
'''

new_adapter_assignment = '''    packet_for_classification = {
        **packet,
        "connected_integrations": connected_integrations or [],
    }
    adapter = (
        packet.get("execution_adapter_target")
        or packet.get("adapter")
        or classify_action_adapter(packet_for_classification)
    )
'''

if old_adapter_assignment not in text:
    raise SystemExit("ADAPTER_ASSIGNMENT_BLOCK_NOT_FOUND")

text = text.replace(old_adapter_assignment, new_adapter_assignment, 1)

target.write_text(text, encoding="utf-8")

test_file = ROOT / "test_provider_aware_adapter_routing.py"
test_file.write_text(r'''
from backend.app.runtime.action_adapter_execution_layer import classify_action_adapter, execute_action_adapter

packet = {
    "implementation_action": "Send governed live email verification through connected email provider",
}

assert classify_action_adapter({**packet, "connected_integrations": ["email"]}) == "stakeholder_interview_outreach_adapter"

result = execute_action_adapter(
    packet,
    tenant_id="client_demo_001",
    connected_integrations=["email"],
    owner_approved=True,
)

assert result["adapter"] == "stakeholder_interview_outreach_adapter"
assert result["performed_actual_action"] is True
assert result.get("actions_performed")

print("PROVIDER_AWARE_ADAPTER_ROUTING_TEST_PASSED")
''', encoding="utf-8")

print("PROVIDER_AWARE_ADAPTER_ROUTING_INSTALLED")
print(f"Backup: {backup_dir}")
print(f"Updated: {target}")
print(f"Created: {test_file}")