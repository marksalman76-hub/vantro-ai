
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
