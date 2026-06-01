
from backend.app.runtime.audio_visual_agent_quality_router import build_audio_visual_quality_plan

ugc = build_audio_visual_quality_plan(
    "ugc_creative_agent",
    "Create UGC video campaign with voiceover, avatar presenter, and video generation."
)

assert ugc["success"] is True
assert ugc["quality_mode"] == "premium_ugc_campaign_runtime"
assert "storyboard" in ugc["deliverable_types"]
assert "elevenlabs" in ugc["recommended_provider_order"]
assert "heygen" in ugc["recommended_provider_order"]
assert ugc["credential_values_exposed"] is False

web = build_audio_visual_quality_plan(
    "website_landing_apps_agent",
    "Create a premium animated landing page with product visuals."
)

assert web["quality_mode"] == "premium_react_site_generation_runtime"
assert "asset_prompt_pack" in web["deliverable_types"]

ads = build_audio_visual_quality_plan(
    "paid_ads_agent",
    "Create paid ads with visual ad prompts and UGC variants."
)

assert ads["quality_mode"] == "premium_ad_creative_runtime"
assert "creative_testing_matrix" in ads["deliverable_types"]

print("AUDIO_VISUAL_AGENT_QUALITY_ROUTER_TEST_PASSED")
print(ugc)
