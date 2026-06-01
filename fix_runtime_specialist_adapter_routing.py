from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "real_action_execution_bridge.py"
BACKUP = ROOT / "backups" / f"runtime_specialist_adapter_routing_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "real_action_execution_bridge.py")

s = TARGET.read_text(encoding="utf-8")

s = s.replace(
'''SAFE_ACTION_ADAPTERS = {
    "create_marketing_asset": "marketing_asset_adapter",
    "create_sales_asset": "sales_asset_adapter",
    "create_email_draft": "email_draft_adapter",
    "create_content_calendar": "content_calendar_adapter",
    "create_research_summary": "research_summary_adapter",
    "create_strategy_document": "strategy_document_adapter",
    "create_client_deliverable": "client_deliverable_adapter",
    "prepare_outreach_draft": "outreach_draft_adapter",
    "prepare_implementation_checklist": "implementation_checklist_adapter",
}''',
'''SAFE_ACTION_ADAPTERS = {
    "create_marketing_asset": "marketing_asset_adapter",
    "create_sales_asset": "sales_asset_adapter",
    "create_email_draft": "email_draft_adapter",
    "create_content_calendar": "content_calendar_adapter",
    "create_research_summary": "research_summary_adapter",
    "create_strategy_document": "strategy_document_adapter",
    "create_client_deliverable": "client_deliverable_adapter",
    "prepare_outreach_draft": "outreach_draft_adapter",
    "prepare_implementation_checklist": "implementation_checklist_adapter",
    "website_draft_page": "website_draft_page_adapter",
    "ads_campaign_draft": "ads_campaign_draft_adapter",
    "seo_content_plan": "seo_deliverable_adapter",
    "store_draft_update": "store_draft_update_adapter",
    "product_copywriting": "product_copywriting_adapter",
}'''
)

s = s.replace(
'''def _normalise_action_type(packet: Dict[str, Any]) -> str:
    raw = " ".join(
        str(packet.get(k, ""))
        for k in ["action_type", "implementation_action", "action", "title", "description"]
    ).lower()

    if "email" in raw:
        return "create_email_draft"
    if "calendar" in raw or "content" in raw:
        return "create_content_calendar"
    if "sales" in raw or "pitch" in raw or "proposal" in raw:
        return "create_sales_asset"
    if "outreach" in raw or "influencer" in raw:
        return "prepare_outreach_draft"
    if "checklist" in raw or "execution plan" in raw or "concrete steps" in raw:
        return "prepare_implementation_checklist"
    if "research" in raw or "market" in raw or "competitor" in raw:
        return "create_research_summary"
    if "strategy" in raw or "positioning" in raw:
        return "create_strategy_document"

    return "create_client_deliverable"''',
'''def _normalise_action_type(packet: Dict[str, Any]) -> str:
    raw = " ".join(
        str(packet.get(k, ""))
        for k in [
            "action_type",
            "implementation_action",
            "action",
            "title",
            "description",
            "user_requested_task",
            "recommended_agent",
            "assigned_agent",
        ]
    ).lower().replace("_", " ")

    assigned_agent = str(packet.get("assigned_agent") or packet.get("recommended_agent") or "").strip().lower()

    if "website draft page" in raw or "landing page" in raw or assigned_agent == "website_landing_apps_agent":
        return "website_draft_page"

    if "ads campaign draft" in raw or "meta ads" in raw or "google ads" in raw or assigned_agent == "paid_ads_agent":
        return "ads_campaign_draft"

    if "seo content plan" in raw or "seo title" in raw or "meta description" in raw or assigned_agent == "seo_agent":
        return "seo_content_plan"

    if "store draft update" in raw or "shopify" in raw or assigned_agent in {"store_builder_agent", "ecommerce_agent"}:
        return "store_draft_update"

    if "product description" in raw or "product copy" in raw or assigned_agent == "product_copywriting_agent":
        return "product_copywriting"

    if "email" in raw:
        return "create_email_draft"
    if "calendar" in raw or "content" in raw:
        return "create_content_calendar"
    if "sales" in raw or "pitch" in raw or "proposal" in raw:
        return "create_sales_asset"
    if "outreach" in raw or "influencer" in raw:
        return "prepare_outreach_draft"
    if "checklist" in raw or "execution plan" in raw or "concrete steps" in raw:
        return "prepare_implementation_checklist"
    if "research" in raw or "market" in raw or "competitor" in raw:
        return "create_research_summary"
    if "strategy" in raw or "positioning" in raw:
        return "create_strategy_document"

    return "create_client_deliverable"'''
)

s = s.replace(
'''    implementation_action = (
        packet.get("implementation_action")
        or packet.get("action")
        or packet.get("description")
        or packet.get("title")
        or "Approved implementation task"
    )''',
'''    implementation_action = (
        packet.get("user_requested_task")
        or packet.get("implementation_action")
        or packet.get("action")
        or packet.get("description")
        or packet.get("title")
        or "Approved implementation task"
    )'''
)

s = s.replace(
'''            "implementation_action": implementation_action,
            "action_type": action_type,
        },''',
'''            "implementation_action": implementation_action,
            "action_type": action_type,
            "execution_adapter_target": adapter,
        },'''
)

TARGET.write_text(s, encoding="utf-8")
print("RUNTIME_SPECIALIST_ADAPTER_ROUTING_FIXED")
print("Backup:", BACKUP)
print("Updated:", TARGET)