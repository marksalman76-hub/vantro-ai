from pathlib import Path
import json
import re

ROOT = Path.cwd()

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

CHECK_FILES = [
    "backend/app/core",
    "backend/app/api",
    "frontend/src/app",
]

REAL_ACTION_KEYWORDS = [
    "send_email",
    "brevo",
    "smtp",
    "ghl",
    "gohighlevel",
    "crm",
    "opportunity",
    "contact",
    "webhook",
    "make",
    "sms",
    "clicksend",
    "shopify",
    "stripe",
    "deploy",
    "publish",
    "post",
    "campaign",
    "execution_adapter",
    "approval",
    "owner_approval",
    "governed",
]

OUTPUT_KEYWORDS = [
    "premium",
    "deliverable",
    "artifact",
    "generated",
    "output",
    "contract",
    "result",
]

def read_all_code():
    chunks = []
    for folder in CHECK_FILES:
        base = ROOT / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix.lower() not in {".py", ".ts", ".tsx", ".js", ".json"}:
                continue
            if "__pycache__" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                chunks.append((str(path.relative_to(ROOT)).replace("\\", "/"), text))
            except Exception:
                pass
    return chunks

def score_agent(agent_id, chunks):
    references = []
    evidence = {
        "referenced": False,
        "premium_output": False,
        "approval_governed": False,
        "real_action_keywords": [],
        "files": [],
    }

    for file, text in chunks:
        if agent_id in text:
            evidence["referenced"] = True
            evidence["files"].append(file)

            lower = text.lower()
            local_real = [kw for kw in REAL_ACTION_KEYWORDS if kw in lower]
            local_output = [kw for kw in OUTPUT_KEYWORDS if kw in lower]

            if local_output:
                evidence["premium_output"] = True

            if "approval" in lower or "owner_approval" in lower or "governed" in lower:
                evidence["approval_governed"] = True

            for kw in local_real:
                if kw not in evidence["real_action_keywords"]:
                    evidence["real_action_keywords"].append(kw)

            references.append(file)

    real_action_count = len(evidence["real_action_keywords"])

    if not evidence["referenced"]:
        status = "NOT_WIRED"
    elif evidence["premium_output"] and evidence["approval_governed"] and real_action_count >= 3:
        status = "LIKELY_REAL_EXECUTION_READY_NEEDS_LIVE_TEST"
    elif evidence["premium_output"] and evidence["approval_governed"]:
        status = "OUTPUT_AND_GOVERNANCE_READY_ADAPTER_NEEDS_CHECK"
    elif evidence["premium_output"]:
        status = "OUTPUT_READY_REAL_ACTION_NOT_CONFIRMED"
    else:
        status = "REFERENCED_ONLY_NOT_READY"

    return {
        "agent_id": agent_id,
        "status": status,
        "referenced": evidence["referenced"],
        "premium_output_evidence": evidence["premium_output"],
        "approval_governance_evidence": evidence["approval_governed"],
        "real_action_keyword_evidence": evidence["real_action_keywords"],
        "matched_file_count": len(set(evidence["files"])),
        "matched_files": sorted(set(evidence["files"]))[:12],
    }

def main():
    chunks = read_all_code()
    results = [score_agent(agent, chunks) for agent in AGENTS]

    summary = {
        "total_agents_checked": len(results),
        "likely_real_execution_ready_needs_live_test": sum(1 for r in results if r["status"] == "LIKELY_REAL_EXECUTION_READY_NEEDS_LIVE_TEST"),
        "output_and_governance_ready_adapter_needs_check": sum(1 for r in results if r["status"] == "OUTPUT_AND_GOVERNANCE_READY_ADAPTER_NEEDS_CHECK"),
        "output_ready_real_action_not_confirmed": sum(1 for r in results if r["status"] == "OUTPUT_READY_REAL_ACTION_NOT_CONFIRMED"),
        "referenced_only_not_ready": sum(1 for r in results if r["status"] == "REFERENCED_ONLY_NOT_READY"),
        "not_wired": sum(1 for r in results if r["status"] == "NOT_WIRED"),
    }

    report = {
        "success": True,
        "audit": "agent_real_execution_readiness",
        "summary": summary,
        "agents": results,
    }

    out = ROOT / "agent_real_execution_readiness_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("AGENT_REAL_EXECUTION_READINESS_AUDIT_COMPLETE")
    print(json.dumps(summary, indent=2))
    print("Report:", out)

    print("\nAGENT STATUS MATRIX")
    for r in results:
        print(f"{r['agent_id']}: {r['status']}")

if __name__ == "__main__":
    main()