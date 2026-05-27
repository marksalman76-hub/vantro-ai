import json
import requests

BASE_URL = "https://app.trance-formation.com.au/api"

token = input("Paste client_token value only: ").strip()
tenant_id = input("Paste tenant_id value: ").strip() or "client_manual_8c187cfb7f"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
    "x-tenant-id": tenant_id,
    "x-actor-role": "client",
    "origin": "https://app.trance-formation.com.au",
    "referer": "https://app.trance-formation.com.au/client",
}

payload = {
    "tenant_id": tenant_id,
    "requested_agent": "ugc_creative_agent",
    "workflow_stage": "ugc_creative",
    "action_type": "create_ugc_video_brief",
    "task": "Generate premium governed AI media content for SK Solutions Group using the AI media generation runtime.",
    "client_portal_action": True,
    "input": {
        "brand_name": "SK Solutions Group",
        "media_type": "ugc video",
        "objective": "premium governed UGC ad generation from client portal",
        "product_or_offer": "AI-powered business automation and multi-agent execution platform",
        "target_platform": "TikTok",
        "region": "Australia",
        "audience": "business owners and operators",
        "benefit": "save time, automate execution, and improve operational output quality",
        "cta": "Book a demo",
        "requested_style": "premium realistic creator-led UGC",
        "brand_colours": ["navy", "white", "indigo"],
        "character_reference": "confident professional creator, natural delivery, consistent face and voice",
        "same_face_required": True,
        "source": "authenticated_client_portal_live_action_test",
    },
    "request": {
        "brand_name": "SK Solutions Group",
        "media_type": "ugc video",
        "objective": "premium governed UGC ad generation from client portal",
        "product_or_offer": "AI-powered business automation and multi-agent execution platform",
        "target_platform": "TikTok",
        "region": "Australia",
        "audience": "business owners and operators",
        "benefit": "save time, automate execution, and improve operational output quality",
        "cta": "Book a demo",
        "requested_style": "premium realistic creator-led UGC",
        "brand_colours": ["navy", "white", "indigo"],
        "character_reference": "confident professional creator, natural delivery, consistent face and voice",
        "same_face_required": True,
        "source": "authenticated_client_portal_live_action_test",
    },
}

response = requests.post(
    f"{BASE_URL}/run-agent",
    headers=headers,
    json=payload,
    timeout=90,
)

print("STATUS", response.status_code)
print("CONTENT_TYPE", response.headers.get("content-type"))

try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)