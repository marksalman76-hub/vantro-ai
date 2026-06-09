from pathlib import Path

TEXT = Path("backend/app/runtime/creative_asset_persistence_bridge.py").read_text(encoding="utf-8")

REQUIRED = [
    '"media_job_id": _truncate(record.get("media_job_id"), 240),',
    '"durable_queue_job_id": _truncate(record.get("durable_queue_job_id"), 240),',
    '"media_pack_id": _truncate(record.get("media_pack_id"), 240),',
    '"media_job_id": _truncate(packet.get("media_job_id") or packet.get("job_id"), 240),',
    '"media_job_id": stored.get("media_job_id"),',
    '"media_job_id": item.get("media_job_id") or (item.get("payload") or {}).get("media_job_id"),',
]

for marker in REQUIRED:
    assert marker in TEXT, marker

print("PERSISTENCE_BRIDGE_CORRELATION_FIELDS_TESTS_PASSED")
