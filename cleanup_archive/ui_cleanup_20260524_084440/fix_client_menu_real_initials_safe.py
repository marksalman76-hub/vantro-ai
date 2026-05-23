from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_real_initials_safe_{stamp}.tsx"
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
  const accountAny = account as any;
  const clientDisplayName =
    accountAny?.company_name ||
    accountAny?.business_name ||
    accountAny?.client_name ||
    accountAny?.contact_name ||
    accountAny?.full_name ||
    accountAny?.email ||
    "Client";
  const clientEmail = accountAny?.email || accountAny?.contact_email || "";
  const clientInitials =
    String(clientDisplayName)
      .split(/\\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join("") || "CL";'''

if anchor not in text:
    raise RuntimeError("Account constants block not found. No changes written.")

text = text.replace(anchor, replacement, 1)

text = text.replace('>PD</summary>', '>{clientInitials}</summary>')
text = text.replace('>PD</div>', '>{clientInitials}</div>')
text = text.replace('>PD</div>', '>{clientInitials}</div>')

text = text.replace(
    '<div style={{ fontWeight: 800, color: "var(--color-dark)" }}>PD</div>',
    '<div style={{ fontWeight: 800, color: "var(--color-dark)" }}>{clientDisplayName}</div>',
)

text = text.replace(
    '<div style={{ fontSize: 12, color: "var(--color-muted)" }}>pd@trance-formation.com.au</div>',
    '<div style={{ fontSize: 12, color: "var(--color-muted)" }}>{clientEmail || accountPackage}</div>',
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_MENU_REAL_INITIALS_SAFE_FIXED")
print(f"Backup: {backup}")