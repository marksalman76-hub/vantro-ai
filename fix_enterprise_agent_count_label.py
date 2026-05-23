from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_enterprise_agent_count_label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

old = '''function getPackageAgentLimitLabel(packageName: string, visibleCount: number) {
  const packageLimit = getPackageAgentLimit(packageName);

  if (packageLimit === null) return `${visibleCount} available`;

  return `${visibleCount}/${packageLimit} active`;
}'''

new = '''function getPackageAgentLimitLabel(packageName: string, visibleCount: number) {
  const normalisedPackage = String(packageName || "").toLowerCase();
  const packageLimit = getPackageAgentLimit(packageName);

  if (normalisedPackage.includes("enterprise")) {
    return `${visibleCount}/${visibleCount} available`;
  }

  if (packageLimit === null) return `${visibleCount} available`;

  return `${visibleCount}/${packageLimit} active`;
}'''

if old not in src:
    raise SystemExit("ERROR: getPackageAgentLimitLabel block not found.")

src = src.replace(old, new, 1)

PAGE.write_text(src, encoding="utf-8")

print("ENTERPRISE_AGENT_COUNT_LABEL_FIXED")
print(f"Backup: {backup}")
print("Enterprise label logic installed:", 'return `${visibleCount}/${visibleCount} available`;' in src)
print("Right column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))