from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

main_path = root / "backend" / "app" / "main.py"

backup = backup_dir / f"main_before_phase_d_quality_target_fix_{timestamp}.py"
backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

text = main_path.read_text(encoding="utf-8")

old = """    polished_output = polish_layer.polish_output(generated_output)

    quality_result = quality_gate.review_output(polished_output)
"""

new = """    polished_output = polish_layer.polish_output(generated_output)

    client_visible_quality_payload = {
        "agent": requested_agent,
        "task": request.task,
        "generated_output": polished_output.get("generated_output")
        or polished_output.get("output")
        or polished_output.get("content")
        or polished_output.get("deliverable")
        or polished_output,
    }

    quality_result = quality_gate.review_output(client_visible_quality_payload)
"""

if old not in text:
    raise RuntimeError("Could not find quality gate target block in main.py")

text = text.replace(old, new)

main_path.write_text(text, encoding="utf-8")

print("PHASE_D_QUALITY_TARGET_FIX_INSTALLED")
print(f"Backup: {backup}")