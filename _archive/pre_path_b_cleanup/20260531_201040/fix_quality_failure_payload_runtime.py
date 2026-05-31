from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
MAIN_FILE = ROOT / "backend" / "app" / "main.py"

BACKUP = ROOT / "backups" / f"quality_failure_payload_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def backup_file(path: Path):
    BACKUP.mkdir(parents=True, exist_ok=True)
    target = BACKUP / path.name
    target.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def main():
    text = MAIN_FILE.read_text(encoding="utf-8", errors="replace")

    if "quality_failure_payload = {" in text:
        print("QUALITY_FAILURE_PAYLOAD_ALREADY_PRESENT")
        return

    marker = "def run_agent("

    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError("run_agent definition not found")

    insert_after = text.find("):", idx)
    if insert_after == -1:
        raise RuntimeError("run_agent signature end not found")

    insert_after += 2

    injection = '''

    quality_failure_payload = {
        "success": False,
        "quality_gate_failed": False,
        "provider_execution_attempted": False,
        "external_action_performed": False,
        "customer_safe": True,
    }

'''

    updated = text[:insert_after] + injection + text[insert_after:]

    backup_file(MAIN_FILE)

    MAIN_FILE.write_text(updated, encoding="utf-8")

    print("QUALITY_FAILURE_PAYLOAD_RUNTIME_FIXED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN_FILE)

if __name__ == "__main__":
    main()