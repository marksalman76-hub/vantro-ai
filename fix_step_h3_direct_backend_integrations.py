from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
backup = BACKUPS / f"client_page_before_step_h3_direct_backend_integrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"

text = client_page.read_text(encoding="utf-8", errors="ignore")
backup.write_text(text, encoding="utf-8")

if "const BACKEND_API_BASE" not in text:
    text = text.replace(
        "const DEFAULT_AGENTS: string[] = [];",
        'const DEFAULT_AGENTS: string[] = [];\nconst BACKEND_API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";',
        1,
    )

text = text.replace('fetch("/api/client-integrations", { cache: "no-store" })', 'fetch(`${BACKEND_API_BASE}/client/integrations`, { cache: "no-store", headers: { "x-tenant-id": account?.tenant_id || "client_demo_001", "x-actor-role": "customer" } })')

text = text.replace('fetch("/api/client-integrations-connect", {', 'fetch(`${BACKEND_API_BASE}/client/integrations/connect`, {')
text = text.replace('fetch("/api/client-integrations-test", {', 'fetch(`${BACKEND_API_BASE}/client/integrations/test`, {')
text = text.replace('fetch("/api/client-integrations-disconnect", {', 'fetch(`${BACKEND_API_BASE}/client/integrations/disconnect`, {')

text = text.replace(
    'headers: { "Content-Type": "application/json" },',
    'headers: { "Content-Type": "application/json", "x-tenant-id": account?.tenant_id || "client_demo_001", "x-actor-role": "customer" },',
)

client_page.write_text(text, encoding="utf-8")

print("STEP_H3_DIRECT_BACKEND_INTEGRATIONS_FIXED")
print(f"Backup: {backup}")