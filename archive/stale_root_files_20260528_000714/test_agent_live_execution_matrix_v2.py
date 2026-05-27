import json
import urllib.request
import urllib.error
from datetime import datetime

BASE_URL = "https://ecommerce-ai-agent-platform-1.onrender.com"

AGENTS = [
    "head_agent",
    "strategist_agent",
    "business_growth_partnerships_agent",
    "lead_generator_appointment_setter_agent",
    "marketing_specialist_agent",
    "social_media_manager_content_creator_agent",
    "seo_agent",
    "email_reply_agent",
    "crm_ai_agent",
    "sales_closer_agent",
    "receptionist_agent",
    "website_landing_apps_agent",
    "product_development_agent",
    "ecommerce_agent",
    "product_research_agent",
    "competitor_intelligence_agent",
    "brand_strategy_agent",
    "store_builder_agent",
    "product_copywriting_agent",
    "ugc_creative_agent",
    "product_image_agent",
    "paid_ads_agent",
    "analytics_optimisation_agent",
    "influencer_collaboration_agent",
    "orchestration_agent",
    "security_compliance_agent",
    "integration_automation_agent",
]

ACTION_TYPE_BY_AGENT = {
    "head_agent": "prepare_analytics_report",
    "strategist_agent": "prepare_analytics_report",
    "business_growth_partnerships_agent": "prepare_analytics_report",
    "lead_generator_appointment_setter_agent": "prepare_email_campaign",
    "marketing_specialist_agent": "create_ad_copy_brief",
    "social_media_manager_content_creator_agent": "create_ad_copy_brief",
    "seo_agent": "prepare_analytics_report",
    "email_reply_agent": "prepare_customer_support_reply",
    "crm_ai_agent": "prepare_customer_support_reply",
    "sales_closer_agent": "prepare_email_campaign",
    "receptionist_agent": "prepare_customer_support_reply",
    "website_landing_apps_agent": "create_landing_page_brief",
    "product_development_agent": "prepare_analytics_report",
    "ecommerce_agent": "create_shopify_product_page",
    "product_research_agent": "prepare_analytics_report",
    "competitor_intelligence_agent": "prepare_analytics_report",
    "brand_strategy_agent": "prepare_analytics_report",
    "store_builder_agent": "create_shopify_product_page",
    "product_copywriting_agent": "create_ad_copy_brief",
    "ugc_creative_agent": "create_ugc_video_brief",
    "product_image_agent": "create_product_image_brief",
    "paid_ads_agent": "launch_paid_campaign",
    "analytics_optimisation_agent": "prepare_analytics_report",
    "influencer_collaboration_agent": "prepare_influencer_outreach",
    "orchestration_agent": "prepare_analytics_report",
    "security_compliance_agent": "prepare_analytics_report",
    "integration_automation_agent": "execute_live_integration_action",
}

def post_json(path, payload):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-tenant-id": "client_manual_admin",
            "x-actor-role": "admin",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return error.code, parsed
    except Exception as error:
        return 0, {"success": False, "error": str(error)}

def classify(result):
    text = json.dumps(result).lower()

    if result.get("success") is not True:
        if "pending_owner_approval" in text or "blocked_pending_owner_approval" in text:
            return "APPROVAL_GATED_READY"
        return "FAILED"

    if "pending_approval" in text or "awaiting_approval" in text or "owner_approval" in text:
        return "APPROVAL_GATED_READY"

    if "executed" in text or "completed" in text or "delivered" in text or "adapter_prepared" in text:
        return "EXECUTION_READY"

    if "output" in text or "deliverable" in text or "artifact" in text:
        return "OUTPUT_READY_NEEDS_ACTION_CONFIRMATION"

    return "SUCCESS_UNCLASSIFIED"

def main():
    results = []

    for agent in AGENTS:
        payload = {
            "tenant_id": "client_manual_admin",
            "requested_agent": agent,
            "workflow_stage": "live_execution_readiness_test",
            "task": "Run a premium live-readiness validation for this ecommerce client. Produce a client-safe result and route any real-world action through owner approval if required.",
            "action_type": ACTION_TYPE_BY_AGENT.get(agent, "prepare_analytics_report"),
            "region": "Australia",
            "language": "English",
            "currency": "AUD",
            "owner_approved": False,
            "execute_real_world_action": True,
            "project_id": "live_readiness_matrix",
            "actor_role": "admin",
            "requested_credits": 1,
            "payload": {
                "tenant_id": "client_manual_admin",
                "integration_key": "crm",
                "action": "readiness_test",
                "payload": {
                    "source": "agent_live_execution_matrix_v2",
                    "note": "Readiness test only. No unsafe live action requested."
                },
                "actor_role": "admin"
            },
        }

        http_status, result = post_json("/run-agent", payload)
        classification = classify(result)

        entry = {
            "agent_id": agent,
            "http_status": http_status,
            "classification": classification,
            "success": result.get("success"),
            "status": result.get("status"),
            "workflow_status": result.get("workflow_status"),
            "execution_status": result.get("execution_status"),
            "error": result.get("error"),
            "message": result.get("message"),
        }
        results.append(entry)
        print(f"{agent}: {classification} HTTP={http_status} status={entry['status']} execution_status={entry['execution_status']} error={entry['error']}")

    summary = {
        "tested_at": datetime.utcnow().isoformat() + "Z",
        "total": len(results),
        "execution_ready": sum(1 for r in results if r["classification"] == "EXECUTION_READY"),
        "approval_gated_ready": sum(1 for r in results if r["classification"] == "APPROVAL_GATED_READY"),
        "output_ready_needs_action_confirmation": sum(1 for r in results if r["classification"] == "OUTPUT_READY_NEEDS_ACTION_CONFIRMATION"),
        "success_unclassified": sum(1 for r in results if r["classification"] == "SUCCESS_UNCLASSIFIED"),
        "failed": sum(1 for r in results if r["classification"] == "FAILED"),
    }

    report = {"success": True, "summary": summary, "results": results}

    with open("agent_live_execution_matrix_report_v2.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\nLIVE EXECUTION MATRIX V2 SUMMARY")
    print(json.dumps(summary, indent=2))
    print("Report: agent_live_execution_matrix_report_v2.json")

if __name__ == "__main__":
    main()