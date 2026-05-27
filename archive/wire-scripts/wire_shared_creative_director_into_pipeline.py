from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()

pipeline_file = ROOT / "backend" / "app" / "runtime" / "ai_media_end_to_end_pipeline.py"

if not pipeline_file.exists():
    raise SystemExit("ai_media_end_to_end_pipeline.py not found")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backups = ROOT / "backups"
backups.mkdir(exist_ok=True)

backup_file = backups / f"ai_media_end_to_end_pipeline_before_creative_director_wire_{timestamp}.py"
backup_file.write_text(
    pipeline_file.read_text(encoding="utf-8"),
    encoding="utf-8"
)

content = pipeline_file.read_text(encoding="utf-8")

IMPORT_BLOCK = '''
from backend.app.runtime.ai_media_creative_director import (
    run_shared_ai_media_creative_director,
    is_ai_media_relevant_agent,
)
'''

if "run_shared_ai_media_creative_director" not in content:
    content = IMPORT_BLOCK.strip() + "\n\n" + content

PIPELINE_INJECTION = r'''
    creative_director_result = None

    if is_ai_media_relevant_agent(agent_id):
        creative_director_result = run_shared_ai_media_creative_director({
            "agent_id": agent_id,
            "brand_name": payload.get("brand_name"),
            "product_name": payload.get("product_name"),
            "target_audience": payload.get("target_audience"),
            "objective": payload.get("objective"),
            "platform": payload.get("platform"),
            "media_type": payload.get("media_type"),
            "language": payload.get("language"),
            "region": payload.get("region"),
        })
'''

TARGET_MARKERS = [
    "quality_gate_result =",
    "provider_packet_result =",
    "execution_packet =",
]

injected = False

for marker in TARGET_MARKERS:
    if marker in content and "creative_director_result = run_shared_ai_media_creative_director" not in content:
        content = content.replace(
            marker,
            PIPELINE_INJECTION + "\n\n    " + marker,
            1
        )
        injected = True
        break

if not injected and "creative_director_result = run_shared_ai_media_creative_director" not in content:
    append_block = r'''

# SHARED AI MEDIA CREATIVE DIRECTOR INTEGRATION
def attach_shared_creative_direction(agent_id: str, payload: dict):
    if not is_ai_media_relevant_agent(agent_id):
        return None

    return run_shared_ai_media_creative_director({
        "agent_id": agent_id,
        "brand_name": payload.get("brand_name"),
        "product_name": payload.get("product_name"),
        "target_audience": payload.get("target_audience"),
        "objective": payload.get("objective"),
        "platform": payload.get("platform"),
        "media_type": payload.get("media_type"),
        "language": payload.get("language"),
        "region": payload.get("region"),
    })
'''
    content += "\n" + append_block

PIPELINE_RESPONSE_APPEND = r'''
    if creative_director_result:
        result["creative_direction"] = creative_director_result
'''

if (
    'result["creative_direction"] = creative_director_result'
    not in content
):
    if "return result" in content:
        content = content.replace(
            "return result",
            PIPELINE_RESPONSE_APPEND + "\n\n    return result",
            1
        )

pipeline_file.write_text(content, encoding="utf-8")

test_file = ROOT / "test_pipeline_creative_director_integration.py"

test_file.write_text(r'''
from pathlib import Path

PIPELINE_FILE = Path("backend/app/runtime/ai_media_end_to_end_pipeline.py")

content = PIPELINE_FILE.read_text(encoding="utf-8")

assert "run_shared_ai_media_creative_director" in content
assert "creative_director_result" in content
assert "creative_direction" in content

print("PIPELINE_CREATIVE_DIRECTOR_INTEGRATION_OK")
'''.strip() + "\n", encoding="utf-8")

print("PIPELINE_SHARED_CREATIVE_DIRECTOR_WIRED")
print(f"Updated: {pipeline_file}")
print(f"Created: {test_file}")