from pathlib import Path

TEXT = Path("backend/app/runtime/shared_creative_media_generation_runtime.py").read_text(encoding="utf-8")

REQUIRED = [
    'media_job_id: str = ""',
    'durable_queue_job_id: str = ""',
    'task_id: str = ""',
    'def _apply_media_job_context_to_asset(',
    '"media_job_id": asset.get("media_job_id") or asset.get("job_id"),',
    'media_job_id=media_job_id,',
    'durable_queue_job_id=durable_queue_job_id,',
    'media_pack_id=pack_id,',
]

for marker in REQUIRED:
    assert marker in TEXT, marker

from backend.app.runtime.shared_creative_media_generation_runtime import _apply_media_job_context_to_asset

asset = {"asset_id": "image_asset_real", "asset_type": "image", "provider": "provider_agnostic"}
patched = _apply_media_job_context_to_asset(
    asset,
    media_job_id="media_job_abc",
    durable_queue_job_id="exec_job_123",
    task_id="media_job_abc",
    media_pack_id="creative_media_pack_xyz",
)

assert patched["media_job_id"] == "media_job_abc"
assert patched["job_id"] == "media_job_abc"
assert patched["task_id"] == "media_job_abc"
assert patched["durable_queue_job_id"] == "exec_job_123"
assert patched["media_pack_id"] == "creative_media_pack_xyz"
assert patched["correlation"]["media_job_id"] == "media_job_abc"

print("SHARED_MEDIA_STACK_CONTEXT_HANDOFF_TESTS_PASSED")
