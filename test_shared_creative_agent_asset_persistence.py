
from backend.app.runtime.creative_asset_persistence_bridge import (
    get_persisted_creative_assets,
    is_creative_agent,
    persist_creative_agent_output,
)

assert is_creative_agent("ugc_creative_agent")
assert is_creative_agent("influencer_collaboration_agent")
assert is_creative_agent("marketing_specialist_agent")
assert not is_creative_agent("crm_ai_agent")

result = persist_creative_agent_output(
    "influencer_collaboration_agent",
    {
        "provider": "internal",
        "title": "Influencer outreach packet for lymphatic massager campaign",
        "summary": "Creator shortlist, UGC brief, outreach messages, usage rights notes, affiliate discount plan.",
        "target_audience": "Women 25-45 interested in wellness and self-care.",
        "quality_score": 91,
    },
)

assert result["success"] is True
assert result["persisted"] is True
assert result["persisted_asset_count"] >= 1
assert result["credential_values_exposed"] is False

assets = get_persisted_creative_assets()
assert assets["success"] is True
assert assets["asset_count"] >= 1
assert assets["credential_values_exposed"] is False

print("SHARED_CREATIVE_AGENT_ASSET_PERSISTENCE_PASSED")
