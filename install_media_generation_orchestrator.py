from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
RUNTIME_DIR = ROOT / "backend" / "app" / "runtime"

TARGET = RUNTIME_DIR / "media_generation_orchestrator.py"
TEST = ROOT / "test_media_generation_orchestrator.py"

BACKUP = ROOT / "backups" / f"media_generation_orchestrator_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)

if TARGET.exists():
    shutil.copy2(TARGET, BACKUP / TARGET.name)

TARGET.write_text(r'''
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any, List

from backend.app.runtime.audio_visual_agent_quality_router import (
    build_audio_visual_quality_plan,
)


def create_media_generation_plan(
    agent_id: str,
    task: str,
    tenant_id: str = "owner_admin",
) -> Dict[str, Any]:

    quality_plan = build_audio_visual_quality_plan(agent_id, task)

    deliverable_types = quality_plan.get("deliverable_types", [])
    providers = quality_plan.get("recommended_provider_order", [])

    media_jobs: List[Dict[str, Any]] = []

    for deliverable in deliverable_types:
        media_jobs.append({
            "job_id": f"media_job_{uuid4().hex[:10]}",
            "deliverable_type": deliverable,
            "recommended_provider_order": providers,
            "execution_mode": "planned_safe_generation",
            "live_generation_enabled": False,
            "customer_safe": True,
        })

    return {
        "success": True,
        "profile": "media_generation_orchestrator_v1",
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "task": task,
        "quality_mode": quality_plan.get("quality_mode"),
        "visual_preview_type": quality_plan.get("visual_preview_type"),
        "media_job_count": len(media_jobs),
        "media_jobs": media_jobs,
        "generation_pipeline": {
            "provider_stack_enabled": True,
            "asset_packet_generation_enabled": True,
            "preview_packet_enabled": True,
            "autonomous_media_planning_enabled": True,
            "live_external_generation_enabled": False,
        },
        "credential_values_exposed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
''', encoding="utf-8")

TEST.write_text(r'''
from backend.app.runtime.media_generation_orchestrator import (
    create_media_generation_plan,
)

ugc = create_media_generation_plan(
    "ugc_creative_agent",
    "Create cinematic luxury skincare UGC videos with creator voiceover."
)

assert ugc["success"] is True
assert ugc["media_job_count"] > 0
assert ugc["generation_pipeline"]["provider_stack_enabled"] is True
assert ugc["generation_pipeline"]["live_external_generation_enabled"] is False

website = create_media_generation_plan(
    "website_landing_apps_agent",
    "Create premium animated website with glassmorphism visuals."
)

assert website["success"] is True
assert website["visual_preview_type"] == "website_preview_packet"

ads = create_media_generation_plan(
    "paid_ads_agent",
    "Create premium paid ads with UGC and visual variants."
)

assert ads["success"] is True
assert ads["media_job_count"] > 0

print("MEDIA_GENERATION_ORCHESTRATOR_TEST_PASSED")
print(ugc)
''', encoding="utf-8")

print("MEDIA_GENERATION_ORCHESTRATOR_INSTALLED")
print("Runtime:", TARGET)
print("Test:", TEST)
print("Backup:", BACKUP)