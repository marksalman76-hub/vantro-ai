from pathlib import Path

target = Path("backend/app/runtime/gold_standard_agent_output_benchmark_runtime.py")

text = target.read_text(encoding="utf-8")

old = '''
        "base_quality_score": base_quality["score"]["quality_score"],
        "base_delivery_status": base_quality["delivery_status"],
        "improvement_required": improvement_required,
'''

new = '''
        "base_quality_score": (
            base_quality.get("score", {}).get("quality_score", 0)
        ),
        "base_delivery_status": (
            base_quality.get("delivery_status")
            or base_quality.get("classified_action")
            or base_quality.get("delivery_action")
            or "unknown"
        ),
        "improvement_required": improvement_required,
'''

if old not in text:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

text = text.replace(old, new)

target.write_text(text, encoding="utf-8")

print("GOLD_STANDARD_DELIVERY_STATUS_COMPAT_FIXED")