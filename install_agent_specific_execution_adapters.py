from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "action_adapter_execution_layer.py"
BACKUP = ROOT / "backups" / f"agent_specific_execution_adapters_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "action_adapter_execution_layer.py")

s = TARGET.read_text(encoding="utf-8")

# Add classification for agent-specific autonomous draft/execution adapters.
s = s.replace(
'''    if any(x in text for x in ["launch campaign", "paid campaign", "increase budget", "ad budget", "go live"]):
        return "approval_gated_campaign_adapter"''',
'''    if any(x in text for x in ["website_draft_page", "landing page", "homepage hero", "web page", "website page"]):
        return "website_draft_page_adapter"

    if any(x in text for x in ["ads_campaign_draft", "meta ads", "google ads", "ad campaign draft", "campaign draft"]):
        return "ads_campaign_draft_adapter"

    if any(x in text for x in ["seo_content_plan", "seo title", "meta description", "organic search"]):
        return "seo_deliverable_adapter"

    if any(x in text for x in ["store_draft_update", "shopify", "product page", "store draft"]):
        return "store_draft_update_adapter"

    if any(x in text for x in ["product description", "product copy", "copywriting"]):
        return "product_copywriting_adapter"

    if any(x in text for x in ["launch campaign", "paid campaign", "increase budget", "ad budget", "go live"]):
        return "approval_gated_campaign_adapter"'''
)

insert_before = '''    elif adapter in {"approval_gated_campaign_adapter", "approval_gated_communication_adapter"}:'''

agent_blocks = r'''
    elif adapter == "website_draft_page_adapter":
        actions = [
            {
                "type": "website_draft_page_created",
                "status": "draft_created",
                "target_system": "website_cms",
                "page_type": "landing_page",
                "record_id": f"web_draft_{uuid4().hex[:10]}",
                "sections": ["hero", "benefits", "product proof", "offer", "faq", "final_cta"],
            }
        ]
        output = """Landing Page Draft Created

Hero Headline:
Luxury Skincare, Crafted for Timeless Radiance

Subheadline:
Premium skincare for Australian women aged 30–50 who want visible glow, deep hydration, and an elevated daily ritual.

Primary CTA:
Shop the Luxury Collection

Landing Page Sections:
1. Hero section — headline, subheadline, CTA, product visual area
2. Problem/aspiration section — dullness, dryness, fine lines, lack of radiance
3. Product benefit section — hydration, firmness, glow, premium ingredients
4. Trust/proof section — ingredient quality, visible-results positioning, testimonials placeholder
5. Launch offer section — 15% first order, sample kit over $150, free express shipping
6. FAQ section — skin type, usage, shipping, returns
7. Final CTA — Begin Your Radiance Ritual

Prepared Draft Page Packet:
- Target system: Website/CMS
- Status: Draft created internally
- Publish status: Not published live
- Owner approval required before public publishing"""

    elif adapter == "ads_campaign_draft_adapter":
        actions = [
            {
                "type": "ads_campaign_draft_created",
                "status": "draft_created",
                "target_system": "ads_platform",
                "platform": "Meta Ads",
                "record_id": f"ads_draft_{uuid4().hex[:10]}",
                "campaign_objective": "sales_or_conversions",
            }
        ]
        output = """Meta Ads Campaign Draft Created

Campaign Objective:
Sales / conversions for luxury skincare launch.

Audience:
Australian women aged 30–50 interested in premium skincare, anti-ageing skincare, luxury beauty, hydration, and self-care.

Ad Variation 1:
Primary Text: Discover luxury skincare designed for radiant, hydrated, timeless skin.
Headline: Reveal Your Radiance
CTA: Shop Now

Ad Variation 2:
Primary Text: Elevate your daily skincare ritual with premium formulas crafted for visible glow.
Headline: Your Ritual, Refined
CTA: Discover More

Ad Variation 3:
Primary Text: Hydration, firmness, and luminosity in one elevated skincare experience.
Headline: Luxury Skincare for Timeless Skin
CTA: Shop the Collection

Budget Recommendation:
Start with a controlled test budget. Owner approval required before spend activation.

Prepared Campaign Packet:
- Target system: Meta Ads
- Status: Draft created internally
- Live spend: Not activated
- Owner approval required before launch"""

    elif adapter == "seo_deliverable_adapter":
        actions = [
            {
                "type": "seo_metadata_created",
                "status": "created",
                "target_system": "website_cms",
                "record_id": f"seo_meta_{uuid4().hex[:10]}",
                "asset_type": "seo_title_meta_description",
            }
        ]
        output = """SEO Deliverable Created

SEO Title:
Luxury Skincare Australia | Premium Radiance Collection

Meta Description:
Discover premium luxury skincare for Australian women aged 30–50. Hydrate, firm, and restore radiant-looking skin with an elevated daily ritual.

Primary Keyword:
luxury skincare Australia

Secondary Keywords:
premium skincare, anti-ageing skincare, skincare for women over 30, radiant skin routine, luxury beauty Australia

Prepared SEO Packet:
- Target system: Website/CMS
- Status: SEO copy created internally
- Publish status: Not published live"""

    elif adapter == "store_draft_update_adapter":
        actions = [
            {
                "type": "store_product_page_draft_created",
                "status": "draft_created",
                "target_system": "store_cms",
                "record_id": f"store_draft_{uuid4().hex[:10]}",
            }
        ]
        output = """Store Draft Update Created

Product Page Draft:
Premium luxury skincare launch product page prepared with hero copy, benefits, offer section, and conversion CTA.

Status:
Draft created internally. Store integration or owner approval required before live publishing."""

    elif adapter == "product_copywriting_adapter":
        actions = [
            {
                "type": "product_copy_created",
                "status": "created",
                "target_system": "copy_asset",
                "record_id": f"copy_{uuid4().hex[:10]}",
            }
        ]
        output = """Product Copy Created

Headline:
Luxury Skincare for Timeless Radiance

Product Description:
Elevate your daily ritual with premium skincare crafted for Australian women seeking hydration, glow, and refined skin confidence. Designed for women aged 30–50, this luxury collection blends elegant sensorial care with high-performance positioning for radiant-looking skin.

Call To Action:
Shop the Collection"""
'''

if agent_blocks.strip() not in s:
    s = s.replace(insert_before, agent_blocks + "\n" + insert_before)

TARGET.write_text(s, encoding="utf-8")
print("AGENT_SPECIFIC_EXECUTION_ADAPTERS_INSTALLED")
print("Backup:", BACKUP)
print("Updated:", TARGET)