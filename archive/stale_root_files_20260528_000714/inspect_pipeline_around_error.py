from pathlib import Path

lines = Path("backend/app/runtime/ai_media_end_to_end_pipeline.py").read_text(encoding="utf-8").splitlines()

for i in range(225, 250):
    print(f"{i+1}: {lines[i]}")