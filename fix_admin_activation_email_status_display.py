from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/admin/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"admin_page_before_activation_email_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old = """                      {deploymentResult.tenant?.activation_link ? (
                        <div>Activation link: {deploymentResult.tenant.activation_link}</div>
                      ) : null}"""

new = """                      {deploymentResult.tenant?.activation_link ? (
                        <div>Activation link: {deploymentResult.tenant.activation_link}</div>
                      ) : null}

                      {deploymentResult.activation_email ? (
                        <div style={{ marginTop: 10 }}>
                          <div>
                            Activation email: {deploymentResult.activation_email.email_sent ? "Sent" : "Not sent"}
                          </div>
                          {deploymentResult.activation_email.recipient ? (
                            <div>Recipient: {deploymentResult.activation_email.recipient}</div>
                          ) : null}
                          {deploymentResult.activation_email.reason ? (
                            <div>Reason: {deploymentResult.activation_email.reason}</div>
                          ) : null}
                          {deploymentResult.activation_email.error ? (
                            <div>Error: {deploymentResult.activation_email.error}</div>
                          ) : null}
                        </div>
                      ) : null}"""

if old not in text:
    raise RuntimeError("Could not find activation link display block.")

text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")

print("ADMIN_ACTIVATION_EMAIL_STATUS_DISPLAY_FIXED")
print(f"Backup: {backup}")