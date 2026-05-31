from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "backend" / "app" / "main.py"
BACKUP = ROOT / "backups" / f"quality_failure_payload_top_init_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

INIT_BLOCK = '''
    quality_failure_payload = {
        "success": False,
        "quality_gate_failed": False,
        "provider_execution_attempted": False,
        "external_action_performed": False,
        "customer_safe": True,
    }

'''

def main():
    text = MAIN.read_text(encoding="utf-8", errors="replace")

    if '"quality_gate_failed": False' in text and text.find('"quality_gate_failed": False') < text.find("quality_result = quality_gate.review_output"):
        print("QUALITY_FAILURE_PAYLOAD_TOP_INIT_ALREADY_PRESENT")
        return

    marker = "def run_agent(request: RunAgentRequest):"
    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError("Exact run_agent signature not found")

    insert_at = text.find("\n", idx) + 1
    if insert_at <= 0:
        raise RuntimeError("Could not find insertion point")

    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP / "main.py").write_text(text, encoding="utf-8")

    text = text[:insert_at] + INIT_BLOCK + text[insert_at:]

    MAIN.write_text(text, encoding="utf-8")

    print("QUALITY_FAILURE_PAYLOAD_TOP_INIT_FIXED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN)

if __name__ == "__main__":
    main()