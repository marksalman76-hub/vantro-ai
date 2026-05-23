from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")

backup = BACKUP_DIR / f"admin_page_before_dynamic_deploy_email_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    'const [deployEmail, setDeployEmail] = useState("admin@acmeconsulting.com");',
    'const [deployEmail, setDeployEmail] = useState("");'
)

old = '''function deployClient() {
    callDeploymentControl(
      "/admin/deployment-control/manual-deploy",
      {
        account_reference: deployTenant,
        company_name: deployCompany,
        contact_email: deployEmail,
        package: "Manual Unlimited",
        active_agents: selectedDeploy,
        unlimited_credits: true,
      },
      "Deploy"
    );
  }'''

new = '''function deployClient() {
    const cleanEmail = deployEmail.trim().toLowerCase();

    if (!cleanEmail || !cleanEmail.includes("@")) {
      showToast("Enter a valid client email before deploying.");
      return;
    }

    callDeploymentControl(
      "/admin/deployment-control/manual-deploy",
      {
        account_reference: deployTenant,
        company_name: deployCompany,
        contact_email: cleanEmail,
        package: "Manual Unlimited",
        active_agents: selectedDeploy,
        unlimited_credits: true,
      },
      "Deploy"
    );
  }'''

if old not in text:
    raise SystemExit("DEPLOY_CLIENT_FUNCTION_TARGET_NOT_FOUND_V2")

text = text.replace(old, new)

text = text.replace(
    '<input value={deployEmail} onChange={(e) => setDeployEmail(e.target.value)} />',
    '<input value={deployEmail} onChange={(e) => setDeployEmail(e.target.value)} placeholder="client@example.com" />'
)

PAGE.write_text(text, encoding="utf-8")

print("ADMIN_DEPLOY_DYNAMIC_EMAIL_V2_FIXED")
print(f"Backup: {backup}")