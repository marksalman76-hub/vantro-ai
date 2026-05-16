from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
BACKEND = ROOT / "backend" / "app"
BACKUPS = ROOT / "backups"

main_file = BACKEND / "main.py"

if not main_file.exists():
    raise FileNotFoundError("backend/app/main.py not found")

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"main_before_step210c_run_agent_credit_gate_bypass_{timestamp}.py"

text = main_file.read_text(encoding="utf-8")
backup.write_text(text, encoding="utf-8")

old = '''    if not credit_gate.get("credit_gate_passed"):
        return {
            "success": False,
            "status": "credit_gate_blocked",
            "message": "Client execution is blocked until credit top-up or next billing cycle.",
            "credit_gate": credit_gate,
        }
'''

new = '''    actor_role = (actor_role or "").strip().lower() if "actor_role" in locals() else ""
    owner_admin_credit_bypass = actor_role in {"owner", "admin", "system"}

    if not credit_gate.get("credit_gate_passed") and not owner_admin_credit_bypass:
        return {
            "success": False,
            "status": "credit_gate_blocked",
            "message": "Client execution is blocked until credit top-up or next billing cycle.",
            "credit_gate": credit_gate,
        }

    if not credit_gate.get("credit_gate_passed") and owner_admin_credit_bypass:
        credit_gate = {
            **credit_gate,
            "credit_gate_passed": True,
            "owner_admin_credit_bypass": True,
            "client_credit_gate_applied": False,
            "bypass_reason": "owner_admin_internal_execution",
        }
'''

if old not in text:
    raise RuntimeError("Expected credit gate block not found. Refusing unsafe edit.")

text = text.replace(old, new)

main_file.write_text(text, encoding="utf-8")
py_compile.compile(str(main_file), doraise=True)

print("STEP_210C_RUN_AGENT_OWNER_CREDIT_GATE_BYPASS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {main_file}")
print("STEP_210C_OK")