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

def post_json(path, payload):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-tenant-id": "client_manual_admin",
            "x-actor-role": "customer",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
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
    if result.get("success") is not True:
        return "FAILED"

    status = str(result.get("workflow_status") or result.get("execution_status") or result.get("status") or "").lower()
    text = json.dumps(result).lower()

    if "pending_approval" in text or "awaiting_approval" in text:
        return "APPROVAL_GATED_READY"

    if "executed" in text or "completed" in text or "delivered" in text:
        return "EXECUTION_READY"

    if "output" in text or "deliverable" in text or "artifact" in text:
        return "OUTPUT_READY_NEEDS_ACTION_CONFIRMATION"

    return "SUCCESS_UNCLASSIFIED"

def main():
    results = []

    for agent in AGENTS:
        payload = {
            "tenant_id": "client_manual_admin",
            "agent_id": agent,
            "task": (
                "Run a premium live-readiness test for this ecommerce client. "
                "Produce a client-safe output and route any real-world action through governed approval if required."
            ),
            "business_context": {
                "company_name": "Manual Deploy Client",
                "industry": "Ecommerce",
                "region": "Australia",
                "target_audience": "online shoppers",
                "goal": "validate premium agent live execution readiness",
            },
            "execution_mode": "live_send",
            "source": "live_execution_readiness_matrix",
        }

        http_status, result = post_json("/run-agent", payload)
        classification = classify(result)

        entry = {
            "agent_id": agent,
            "http_status": http_status,
            "classification": classification,
            "success": result.get("success"),
            "workflow_status": result.get("workflow_status"),
            "execution_status": result.get("execution_status"),
            "status": result.get("status"),
            "message": result.get("message") or result.get("error"),
        }
        results.append(entry)
        print(f"{agent}: {classification} HTTP={http_status}")

    summary = {
        "tested_at": datetime.utcnow().isoformat() + "Z",
        "total": len(results),
        "execution_ready": sum(1 for r in results if r["classification"] == "EXECUTION_READY"),
        "approval_gated_ready": sum(1 for r in results if r["classification"] == "APPROVAL_GATED_READY"),
        "output_ready_needs_action_confirmation": sum(1 for r in results if r["classification"] == "OUTPUT_READY_NEEDS_ACTION_CONFIRMATION"),
        "success_unclassified": sum(1 for r in results if r["classification"] == "SUCCESS_UNCLASSIFIED"),
        "failed": sum(1 for r in results if r["classification"] == "FAILED"),
    }

    report = {
        "success": True,
        "summary": summary,
        "results": results,
    }

    with open("agent_live_execution_matrix_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\nLIVE EXECUTION MATRIX SUMMARY")
    print(json.dumps(summary, indent=2))
    print("Report: agent_live_execution_matrix_report.json")

if __name__ == "__main__":
    main()