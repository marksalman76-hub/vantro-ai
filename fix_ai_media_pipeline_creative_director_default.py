from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
pipeline_file = ROOT / "backend" / "app" / "runtime" / "ai_media_end_to_end_pipeline.py"

if not pipeline_file.exists():
    raise SystemExit("ai_media_end_to_end_pipeline.py not found")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = backups / f"ai_media_end_to_end_pipeline_before_creative_director_default_fix_{timestamp}.py"
backup_file.write_text(pipeline_file.read_text(encoding="utf-8"), encoding="utf-8")

content = pipeline_file.read_text(encoding="utf-8")

needle = "def run_ai_media_end_to_end_pipeline("
start = content.find(needle)
if start == -1:
    raise SystemExit("run_ai_media_end_to_end_pipeline function not found")

body_start = content.find(":", start)
if body_start == -1:
    raise SystemExit("function body start not found")

insert_point = content.find("\n", body_start) + 1

if "    creative_director_result = None\n" not in content[start: start + 1500]:
    content = content[:insert_point] + "    creative_director_result = None\n" + content[insert_point:]

pipeline_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_ai_media_pipeline_creative_director_default.py"
test_file.write_text(r'''
from backend.app.runtime.ai_media_end_to_end_pipeline import run_ai_media_end_to_end_pipeline


def main():
    result = run_ai_media_end_to_end_pipeline(
        tenant_id="tenant_test",
        agent_id="ugc_video_agent",
        brand_name="Default Fix Brand",
        product_name="Default Fix Product",
        target_audience="online shoppers",
        objective="premium UGC ad",
        platform="TikTok",
        media_type="ugc video",
        language="English",
        region="global",
        context={},
    )

    assert isinstance(result, dict)
    assert result.get("status") or result.get("success") is not None

    print("AI_MEDIA_PIPELINE_CREATIVE_DIRECTOR_DEFAULT_OK")


if __name__ == "__main__":
    main()
'''.strip() + "\n", encoding="utf-8")

print("AI_MEDIA_PIPELINE_CREATIVE_DIRECTOR_DEFAULT_FIXED")
print(f"Backup: {backup_file}")
print(f"Updated: {pipeline_file}")
print(f"Created: {test_file}")