from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP = ROOT / "backups" / f"quality_failure_payload_top_init_v2_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

INIT_BLOCK = '''    quality_failure_payload = {
        "success": False,
        "quality_gate_failed": False,
        "provider_execution_attempted": False,
        "external_action_performed": False,
        "customer_safe": True,
    }

'''

def main():
    text = MAIN.read_text(encoding="utf-8", errors="replace")

    run_idx = text.find("def run_agent")
    if run_idx == -1:
        raise RuntimeError("run_agent not found")

    quality_idx = text.find("quality_result = quality_gate.review_output", run_idx)
    existing_top_idx = text.find('"quality_gate_failed": False', run_idx)

    if existing_top_idx != -1 and quality_idx != -1 and existing_top_idx < quality_idx:
        print("QUALITY_FAILURE_PAYLOAD_TOP_INIT_ALREADY_PRESENT")
        return

    signature_end = text.find("\n", run_idx)
    if signature_end == -1:
        raise RuntimeError("run_agent signature line end not found")

    insert_at = signature_end + 1

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / "main.py").write_text(text, encoding="utf-8")

    updated = text[:insert_at] + INIT_BLOCK + text[insert_at:]
    MAIN.write_text(updated, encoding="utf-8")

    print("QUALITY_FAILURE_PAYLOAD_TOP_INIT_V2_FIXED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN)

if __name__ == "__main__":
    main()