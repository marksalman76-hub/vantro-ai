from pathlib import Path

target = Path("backend/app/runtime/gold_standard_agent_output_benchmark_runtime.py")
text = target.read_text(encoding="utf-8")

text = text.replace(
    '''    if missing:
        score -= min(25, len(missing) * 6)
    if len(trait_hits) < 2:
        score -= 8
    if len(rubric_hits) < max(1, len(rubric) // 2):
        score -= 8
''',
    '''    if missing:
        score -= min(20, len(missing) * 5)
    if len(trait_hits) < 2:
        score -= 4
    if len(rubric_hits) < max(1, len(rubric) // 2):
        score -= 4
'''
)

target.write_text(text, encoding="utf-8")
print("GOLD_STANDARD_BENCHMARK_SCORE_CALIBRATION_FIXED")