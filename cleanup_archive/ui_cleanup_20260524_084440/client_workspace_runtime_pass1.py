from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_runtime_pass1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    "  client_id?: string;\n",
    "  client_id?: string;\n  tenant_id?: string;\n"
)

text = text.replace(
    'const BACKEND_API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";',
    'const BACKEND_API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.trance-formation.com.au";'
)

text = text.replace(
    'const accountPackage = account?.package_name || account?.package || "Active workspace";',
    '''const tenantId = account?.tenant_id || account?.client_id || "unknown_client";
  const accountPackage = account?.package_name || account?.package || "Active workspace";
  const accountStatus = account?.status || "active";
  const activeAgentCount = account?.active_agents?.length || 0;'''
)

text = text.replace(
    'account?.client_id ||\n        "client_manual_admin";',
    'tenantId;'
)

text = text.replace(
    '"x-tenant-id": "client_demo_001"',
    '"x-tenant-id": tenantId'
)

text = text.replace(
    '["Workspace status", "Ready for execution", accountPackage],',
    '["Workspace status", accountStatus === "active" ? "Ready for execution" : accountStatus, accountPackage],'
)

text = text.replace(
    '["Workflows", liveDeliverable ? "1 tracked" : "0 tracked", liveDeliverable ? "Latest execution" : "No active workflow"],',
    '["Agents", String(activeAgentCount), activeAgentCount ? "Active in this workspace" : "No active agents"],'
)

text = text.replace(
    'niche: "Saved client business profile",',
    'niche: businessProfile.business_niche || "Saved client business profile",'
)

text = text.replace(
    'target_audience: "Saved target audience and customer context",',
    'target_audience: businessProfile.target_audience || "Saved target audience and customer context",'
)

text = text.replace(
    'positioning: "Client-specific commercial positioning and execution requirements",',
    'positioning: businessProfile.notes || "Client-specific commercial positioning and execution requirements",'
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_WORKSPACE_RUNTIME_PASS1_INSTALLED")
print(f"Backup: {backup}")