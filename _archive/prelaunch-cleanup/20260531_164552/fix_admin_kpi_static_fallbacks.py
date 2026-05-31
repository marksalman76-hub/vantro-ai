from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "admin" / "page.tsx"

backup_dir = root / "backups" / f"admin_kpi_static_fallbacks_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

replacements = {
    "runtime?.execution_summary?.successful_executions || 148": "runtime?.execution_summary?.successful_executions ?? 0",
    "runtime?.execution_summary?.pending_approvals || 2": "runtime?.execution_summary?.pending_approvals ?? 0",
    "runtime?.execution_summary?.blocked_executions || 6": "runtime?.execution_summary?.blocked_executions ?? 0",
    "runtime?.execution_summary?.premium_outputs_generated || 221": "runtime?.execution_summary?.premium_outputs_generated ?? 0",
    "runtime?.billing_summary?.subscriptions_active || 8": "runtime?.billing_summary?.subscriptions_active ?? 0",
    "runtime?.billing_summary?.credits_remaining || 1188": "runtime?.billing_summary?.credits_remaining ?? 0",
    "orchestration?.routes?.count || 0": "orchestration?.routes?.count ?? 0",
    "orchestration?.liveExecutions?.count || 0": "orchestration?.liveExecutions?.count ?? 0",
    "orchestration?.deadLetters?.count || 0": "orchestration?.deadLetters?.count ?? 0",
    "orchestration?.manualReview?.count || 0": "orchestration?.manualReview?.count ?? 0",
}

missing = []

for old, new in replacements.items():
    if old not in text:
        missing.append(old)
    text = text.replace(old, new)

target.write_text(text, encoding="utf-8")

print("ADMIN_KPI_STATIC_FALLBACKS_REMOVED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")
if missing:
    print("Missing patterns:")
    for item in missing:
        print("-", item)