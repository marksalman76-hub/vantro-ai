from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_registry_function_clean_{timestamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

start = text.index("  async function loadClientRegistry() {")
end = text.index("  async function callDeploymentControl", start)

replacement = '''  async function loadClientRegistry() {
    try {
      const response = await fetch("/api/admin-deployment-control", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: "/admin/deployment-control/list?limit=25",
          method: "GET",
        }),
      });

      const data = await response.json();
      setClientRegistry(data.tenants || []);
    } catch {
      setClientRegistry([]);
    }

    try {
      const response = await fetch("/api/admin-deployment-control", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: "/admin/deployment-control/summary",
          method: "GET",
        }),
      });

      const data = await response.json();
      setClientRegistrySummary(data);
    } catch {
      setClientRegistrySummary(null);
    }
  }

'''

text = text[:start] + replacement + text[end:]

PAGE.write_text(text, encoding="utf-8")

print("ADMIN_REGISTRY_FUNCTION_CLEAN_FIXED")
print(f"Backup: {backup}")