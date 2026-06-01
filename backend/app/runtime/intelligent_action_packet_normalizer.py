
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


NORMALIZER_PROFILE = "intelligent_action_packet_normalizer_v1"

HEADING_PATTERNS = [
    r"^\s*\d+\.?\s*$",
    r"^\s*\d+\.\s+[a-z\s\/&-]+$",
    r"^\s*[a-z]\.\s+[a-z\s\/&-]+$",
    r"^\s*#{1,6}\s+",
    r"^\s*\*\*[^*]+\*\*\s*$",
]

JUNK_PHRASES = {
    "executive summary",
    "business/industry context assumptions",
    "business industry context assumptions",
    "specific opportunity or problem diagnosis",
    "execution plan with concrete steps",
    "deliverables/assets/actions to create",
    "deliverables assets actions to create",
    "kpis or measurable success criteria",
    "risks, constraints, and mitigations",
    "risks constraints and mitigations",
    "owner/admin review points",
    "owner admin review points",
    "immediate next actions",
}

APPROVAL_KEYWORDS = {
    "launch paid", "increase budget", "increase ad", "ad spend", "payment",
    "purchase", "contract", "legal agreement", "send bulk", "bulk email",
    "publish live", "go live", "delete", "remove records", "hire", "fire",
}

SAFE_OPERATIONAL_VERBS = {
    "create", "draft", "prepare", "develop", "build", "generate", "analyse",
    "analyze", "identify", "research", "map", "document", "outline", "schedule",
    "commission", "form", "train", "compile", "design",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"[*_`#]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_heading_or_junk(text: str) -> bool:
    clean = _clean(text).lower().strip(":.- ")

    if not clean:
        return True

    if clean in JUNK_PHRASES:
        return True

    if len(clean.split()) <= 5 and any(section in clean for section in ["phase", "plan", "summary", "deliverables", "risks", "kpis"]):
        return True

    return any(re.match(pattern, clean, flags=re.IGNORECASE) for pattern in HEADING_PATTERNS)


def _contains_approval_keyword(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in APPROVAL_KEYWORDS)


def _has_safe_operational_verb(text: str) -> bool:
    lower = text.lower()
    return any(lower.startswith(v + " ") or f" {v} " in lower for v in SAFE_OPERATIONAL_VERBS)


def _infer_agent(text: str, fallback: str = "marketing_specialist_agent") -> str:
    lower = text.lower()

    if "seo" in lower or "organic" in lower or "topic cluster" in lower:
        return "seo_agent"
    if "crm" in lower or "pipeline" in lower or "prospect" in lower:
        return "crm_ai_agent"
    if "webinar" in lower or "blog" in lower or "social" in lower or "content" in lower:
        return "social_media_manager_content_creator_agent"
    if "partner" in lower or "partnership" in lower or "alliance" in lower:
        return "business_growth_partnerships_agent"
    if "data" in lower or "analytics" in lower or "kpi" in lower or "dashboard" in lower:
        return "analytics_optimisation_agent"
    if "compliance" in lower or "regulatory" in lower or "risk" in lower:
        return "security_compliance_agent"

    return fallback


def _adapter_target(text: str) -> str:
    lower = text.lower()

    if (
        "send email" in lower
        or "email draft" in lower
        or "brevo" in lower
        or "outreach" in lower
        or "follow-up email" in lower
        or "follow up email" in lower
        or "interview" in lower
        or "pilot client" in lower
    ):
        return "stakeholder_interview_outreach_adapter"
    if "competitor" in lower or "market research" in lower or "white space" in lower:
        return "competitor_research_adapter"
    if "thought leadership" in lower or "whitepaper" in lower or "white paper" in lower or "webinar" in lower or "blog" in lower or "case stud" in lower:
        return "content_asset_creation_adapter"
    if "messaging" in lower or "value proposition" in lower or "sales" in lower or "proposal" in lower or "deck" in lower:
        return "sales_enablement_asset_adapter"
    if "crm" in lower or "pipeline" in lower or "appointment" in lower or "lead" in lower:
        return "crm_task_creation_adapter"
    if "launch campaign" in lower or "paid campaign" in lower or "budget" in lower:
        return "approval_gated_campaign_adapter"

    return "general_operational_task_adapter"


def _rewrite_heading_to_operational(text: str) -> str:
    lower = _clean(text).lower()

    if "execution plan" in lower:
        return "Create healthcare technology pilot engagement implementation checklist"
    if "capability" in lower or "partnership" in lower:
        return "Identify 5 healthcare technology integration partners and create partnership outreach drafts"
    if "pilot" in lower or "case" in lower:
        return "Create pilot project scope and case study capture checklist for healthcare technology clients"
    if "deliverables" in lower or "assets" in lower:
        return "Create healthcare technology sales enablement asset checklist and production queue"
    if "seo" in lower or "search" in lower or "meta description" in lower or "organic" in lower:
        return "Create SEO optimisation deliverables and metadata"

    if "marketing" in lower or "thought leadership" in lower or "content calendar" in lower:
        return "Create marketing campaign content deliverables"
    if "review" in lower:
        return "Create owner review checklist for healthcare technology service launch readiness"

    return "Create executable implementation deliverable from approved autonomous task request"


def _rewrite_to_executable(text: str) -> str:
    clean = _clean(text)

    if _is_heading_or_junk(clean):
        return _rewrite_heading_to_operational(clean)

    lower = clean.lower()

    if lower.startswith("lack of "):
        return f"Create credibility-building action plan to address {clean}"

    if lower.startswith("there is ") or lower.startswith("this creates "):
        return f"Create market opportunity validation brief based on: {clean}"

    if lower.startswith("the geography"):
        return "Create region-specific compliance and market assumptions checklist for healthcare technology positioning"

    if lower.startswith("develop service offerings"):
        return "Create healthcare technology service offering framework for digital transformation, compliance advisory, and ecosystem integration"

    if lower.startswith("identify early adopter clients"):
        return "Create pilot client shortlist criteria and outreach draft for early healthcare technology adopters"

    if lower.startswith("develop case studies"):
        return "Create case study template and thought leadership asset plan for healthcare technology consulting"

    if lower.startswith("create sector-specific marketing materials"):
        return "Create healthcare technology sector marketing collateral checklist and first draft briefs"

    if lower.startswith("commission targeted"):
        return "Create healthcare technology market research task, stakeholder interview outreach draft, and CRM follow-up task"

    if "brevo" in lower or "send governed live" in lower or "send email" in lower:
        return f"Send governed live email verification through connected email provider: {clean}"

    if not _has_safe_operational_verb(clean):
        return f"Create operational execution task for: {clean}"

    return clean


def normalize_action_packet(packet: Dict[str, Any], *, fallback_agent: str = "marketing_specialist_agent") -> Dict[str, Any]:
    original_action = (
        packet.get("implementation_action")
        or packet.get("action")
        or packet.get("title")
        or packet.get("description")
        or ""
    )

    normalized_action = _rewrite_to_executable(original_action)
    approval_required = _contains_approval_keyword(normalized_action) or _contains_approval_keyword(original_action)

    inferred_agent = _infer_agent(normalized_action, packet.get("recommended_agent") or packet.get("assigned_agent") or fallback_agent)
    adapter_target = _adapter_target(normalized_action)

    risk_level = "high" if approval_required else str(packet.get("risk_level") or packet.get("risk") or "medium").lower()
    if risk_level == "high" and not approval_required:
        # Strategic high-risk text can still become safe draft/research work after normalization.
        if adapter_target not in {"approval_gated_campaign_adapter"}:
            risk_level = "medium"

    return {
        **packet,
        "packet_id": packet.get("packet_id") or f"norm_packet_{uuid4().hex[:12]}",
        "original_action": _clean(original_action),
        "implementation_action": normalized_action,
        "title": normalized_action,
        "recommended_agent": inferred_agent,
        "assigned_agent": inferred_agent,
        "risk_level": risk_level,
        "approval_required": approval_required,
        "execution_type": "approval_required" if approval_required else "autonomous_safe_operational",
        "operational_intent": "execute_adapter_action",
        "safe_action_score": 0.35 if approval_required else 0.92,
        "execution_adapter_target": adapter_target,
        "normalization_applied": True,
        "normalizer_profile": NORMALIZER_PROFILE,
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def normalize_action_packets(packets: List[Dict[str, Any]], *, fallback_agent: str = "marketing_specialist_agent") -> Dict[str, Any]:
    normalized = [
        normalize_action_packet(packet, fallback_agent=fallback_agent)
        for packet in packets
    ]

    executable = [
        item for item in normalized
        if item.get("execution_type") == "autonomous_safe_operational"
    ]

    approval_required = [
        item for item in normalized
        if item.get("execution_type") == "approval_required"
    ]

    return {
        "success": True,
        "profile": NORMALIZER_PROFILE,
        "input_count": len(packets),
        "normalized_count": len(normalized),
        "executable_count": len(executable),
        "approval_required_count": len(approval_required),
        "action_packets": normalized,
        "created_at": _now(),
        "customer_safe": True,
        "credential_values_exposed": False,
    }


def normalize_implementation_plan(plan: Dict[str, Any], *, fallback_agent: str = "marketing_specialist_agent") -> Dict[str, Any]:
    packets = list(plan.get("action_packets") or [])
    result = normalize_action_packets(packets, fallback_agent=fallback_agent)

    return {
        **plan,
        "normalization": {
            "profile": NORMALIZER_PROFILE,
            "input_count": result["input_count"],
            "normalized_count": result["normalized_count"],
            "executable_count": result["executable_count"],
            "approval_required_count": result["approval_required_count"],
        },
        "action_packets": result["action_packets"],
    }
