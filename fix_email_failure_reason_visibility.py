from pathlib import Path

p = Path("backend/app/core/admin_deployment_control_runtime.py")
s = p.read_text(encoding="utf-8")

s = s.replace(
    '''        "reason": email_result.get("reason"),
        "recipient": contact_email,''',
    '''        "reason": email_result.get("reason"),
        "error": email_result.get("error"),
        "recipient": contact_email,''',
)

p.write_text(s, encoding="utf-8")
print("EMAIL_FAILURE_REASON_VISIBILITY_FIXED")