from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
normalizer_file = ROOT / "backend" / "app" / "runtime" / "intelligent_action_packet_normalizer.py"

backup_dir = ROOT / "backups" / f"email_adapter_intent_routing_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(normalizer_file, backup_dir / normalizer_file.name)

text = normalizer_file.read_text(encoding="utf-8")

old_adapter_target = '''def _adapter_target(text: str) -> str:
    lower = text.lower()

    if "interview" in lower or "outreach" in lower or "pilot client" in lower:
        return "stakeholder_interview_outreach_adapter"
'''

new_adapter_target = '''def _adapter_target(text: str) -> str:
    lower = text.lower()

    if (
        "send email" in lower
        or "email draft" in lower
        or "brevo" in lower
        or "outreach" in lower
        or "follow-up email" in lower
        or "follow up email" in lower
        or "interview" in lower
        or "pilot client" in lower
    ):
        return "stakeholder_interview_outreach_adapter"
'''

if old_adapter_target not in text:
    raise SystemExit("ADAPTER_TARGET_BLOCK_NOT_FOUND")

text = text.replace(old_adapter_target, new_adapter_target)

old_rewrite_tail = '''    if not _has_safe_operational_verb(clean):
        return f"Create operational execution task for: {clean}"

    return clean
'''

new_rewrite_tail = '''    if "brevo" in lower or "send governed live" in lower or "send email" in lower:
        return f"Send governed live email verification through connected email provider: {clean}"

    if not _has_safe_operational_verb(clean):
        return f"Create operational execution task for: {clean}"

    return clean
'''

if old_rewrite_tail not in text:
    raise SystemExit("REWRITE_TAIL_BLOCK_NOT_FOUND")

text = text.replace(old_rewrite_tail, new_rewrite_tail)

normalizer_file.write_text(text, encoding="utf-8")

test_file = ROOT / "test_email_adapter_intent_routing.py"
test_file.write_text(r'''
from backend.app.runtime.intelligent_action_packet_normalizer import normalize_action_packet

packet = {
    "packet_id": "email_route_001",
    "recommended_agent": "email_reply_agent",
    "title": "Send governed live Brevo execution verification email",
    "risk_level": "medium",
    "approval_required": False,
}

result = normalize_action_packet(packet)

assert result["execution_adapter_target"] == "stakeholder_interview_outreach_adapter"
assert "email" in result["implementation_action"].lower()
assert result["execution_type"] == "autonomous_safe_operational"
assert result["approval_required"] is False

print("EMAIL_ADAPTER_INTENT_ROUTING_TEST_PASSED")
''', encoding="utf-8")

print("EMAIL_ADAPTER_INTENT_ROUTING_FIXED")
print(f"Backup: {backup_dir}")
print(f"Updated: {normalizer_file}")
print(f"Created: {test_file}")