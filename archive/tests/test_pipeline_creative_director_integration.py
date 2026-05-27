from pathlib import Path

PIPELINE_FILE = Path("backend/app/runtime/ai_media_end_to_end_pipeline.py")

content = PIPELINE_FILE.read_text(encoding="utf-8")

assert "run_shared_ai_media_creative_director" in content
assert "creative_director_result" in content
assert "creative_direction" in content

print("PIPELINE_CREATIVE_DIRECTOR_INTEGRATION_OK")
