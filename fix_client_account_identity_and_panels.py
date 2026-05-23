from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_account_identity_panels_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

anchor = '''  const creditsRemaining = account?.credits_remaining ?? 0;
  const tenantId = account?.tenant_id || account?.client_id || "unknown_client";
  const accountPackage = account?.package_name || account?.package || "Active workspace";
  const accountStatus = account?.status || "active";
  const activeAgentCount = account?.active_agents?.length || 0;'''

replacement = '''  const creditsRemaining = account?.credits_remaining ?? 0;
  const tenantId = account?.tenant_id || account?.client_id || "unknown_client";
  const accountPackage = account?.package_name || account?.package || "Active workspace";
  const accountStatus = account?.status || "active";
  const activeAgentCount = account?.active_agents?.length || 0;
  const clientDisplayName =
    account?.company_name ||
    account?.business_name ||
    account?.client_name ||
    account?.name ||
    account?.email ||
    "Client";
  const clientEmail = account?.email || account?.contact_email || "";
  const clientInitials = String(clientDisplayName)
    .split(/\\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "CL";
  const activeAccount =
    accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing";'''

if anchor not in text:
    raise RuntimeError("Account constants block not found.")

text = text.replace(anchor, replacement, 1)

text = text.replace('PD</div>', '{clientInitials}</div>')
text = text.replace('>PD</summary>', '>{clientInitials}</summary>')
text = text.replace('>PD</div>', '>{clientInitials}</div>')
text = text.replace('<div style={{ fontWeight: 800, color: "var(--color-dark)" }}>PD</div>', '<div style={{ fontWeight: 800, color: "var(--color-dark)" }}>{clientDisplayName}</div>')
text = text.replace('<div style={{ fontSize: 12, color: "var(--color-muted)" }}>pd@trance-formation.com.au</div>', '<div style={{ fontSize: 12, color: "var(--color-muted)" }}>{clientEmail || accountPackage}</div>')

text = text.replace(
'''window.location.hash = "settings";
                    alert("Settings panel selected.");''',
'''window.location.hash = "account-settings";'''
)

text = text.replace(
'''window.location.hash = "profile";
                    alert("Profile panel selected.");''',
'''window.location.hash = "account-profile";'''
)

text = text.replace(
'''window.location.hash = "password-reset";
                    alert("Password reset selected.");''',
'''window.location.hash = "password-reset";'''
)

text = text.replace(
'''window.location.hash = "two-factor-authentication";
                    alert("2FA selected.");''',
'''window.location.hash = "two-factor-authentication";'''
)

text = text.replace(
'accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing"',
'activeAccount'
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_ACCOUNT_IDENTITY_AND_PANELS_FIXED")
print(f"Backup: {backup}")