from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()

target = root / "frontend" / "src" / "app" / "api" / "admin-runtime" / "route.ts"

backup_dir = root / "backups" / f"admin_runtime_seeded_metrics_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(target, backup_dir / "route.ts")

text = target.read_text(encoding="utf-8")

old_execution = """    execution_summary: {
      active_workflows: 12,
      pending_approvals: 2,
      successful_executions: 148,
      blocked_executions: 6,
      failed_executions: 1,
      premium_outputs_generated: 221,
    },"""

new_execution = """    execution_summary: {
      active_workflows:
        operationalDashboard?.data?.execution_summary?.active_workflows ?? 0,

      pending_approvals:
        operationalDashboard?.data?.execution_summary?.pending_approvals ?? 0,

      successful_executions:
        operationalDashboard?.data?.execution_summary?.successful_executions ?? 0,

      blocked_executions:
        operationalDashboard?.data?.execution_summary?.blocked_executions ?? 0,

      failed_executions:
        operationalDashboard?.data?.execution_summary?.failed_executions ?? 0,

      premium_outputs_generated:
        operationalDashboard?.data?.execution_summary?.premium_outputs_generated ?? 0,
    },"""

old_billing = """    billing_summary: {
      subscriptions_active: 8,
      subscriptions_past_due: 1,
      credits_consumed: 412,
      credits_remaining: 1188,
      topup_runtime: "ready",
      stripe_live_ready: true,
    },"""

new_billing = """    billing_summary: {
      subscriptions_active:
        billingReadiness?.data?.subscriptions_active ?? 0,

      subscriptions_past_due:
        billingReadiness?.data?.subscriptions_past_due ?? 0,

      credits_consumed:
        billingReadiness?.data?.credits_consumed ?? 0,

      credits_remaining:
        billingReadiness?.data?.credits_remaining ?? 0,

      topup_runtime:
        billingReadiness?.data?.topup_runtime ?? "ready",

      stripe_live_ready:
        billingReadiness?.data?.stripe_live_ready ?? false,
    },"""

if old_execution not in text:
    raise SystemExit("execution_summary block not found")

if old_billing not in text:
    raise SystemExit("billing_summary block not found")

text = text.replace(old_execution, new_execution)
text = text.replace(old_billing, new_billing)

target.write_text(text, encoding="utf-8")

print("ADMIN_RUNTIME_SEEDED_METRICS_FIXED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")