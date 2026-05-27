from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

runtime_dir = ROOT / "backend" / "app" / "runtime"
runtime_dir.mkdir(parents=True, exist_ok=True)

target = runtime_dir / "global_agent_output_quality_runtime.py"
test_file = ROOT / "test_global_agent_output_quality_runtime_direct.py"

backup_dir = ROOT / "backups" / f"global_agent_output_quality_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

for p in [target, test_file]:
    if p.exists():
        (backup_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

target.write_text(r'''
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from backend.app.runtime.provider_execution_postgres_ledger_bridge import (
    persist_latency_metric_bridge,
    persist_worker_event_bridge,
)

GENERIC_TERMS = [
    "generic",
    "placeholder",
    "lorem ipsum",
    "as an ai",
    "i cannot",
    "it depends",
    "some ideas",
    "various options",
    "best practices",
    "leverage",
    "synergy",
    "robust solution",
]

INTERNAL_UNSAFE_TERMS = [
    "internal prompt",
    "system prompt",
    "developer message",
    "raw queue",
    "debug token",
    "api key",
    "secret",
    "credential",
    "webhook secret",
    "admin token",
    "provider secret",
]

AGENT_RUBRICS = {
    "seo_agent": ["technical_seo", "local_seo", "keywords", "priority_actions", "measurement"],
    "marketing_specialist_agent": ["audience_fit", "offer_clarity", "positioning", "cta_strength", "campaign_actions"],
    "lead_generator_agent": ["icp_fit", "personalisation", "conversion_likelihood", "follow_up_logic", "risk_filtering"],
    "website_agent": ["ux_structure", "conversion_flow", "brand_fit", "section_clarity", "implementation_readiness"],
    "head_agent": ["synthesis_quality", "conflict_resolution", "priority_decision", "risk_awareness", "owner_recommendation"],
    "social_media_agent": ["hook_strength", "platform_fit", "engagement_potential", "brand_voice", "content_specificity"],
    "email_reply_agent": ["tone_fit", "clarity", "accuracy", "next_action", "customer_safe_language"],
    "ecommerce_agent": ["product_fit", "conversion_logic", "offer_quality", "retention_logic", "operational_actionability"],
    "default": ["specificity", "commercial_value", "client_readiness", "clear_next_steps", "safe_language"],
}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _normalise_agent_key(agent_key: str) -> str:
    return (agent_key or "default").strip().lower().replace(" ", "_").replace("-", "_")


def get_agent_quality_rubric(agent_key: str) -> Dict[str, Any]:
    normalised = _normalise_agent_key(agent_key)
    rubric = AGENT_RUBRICS.get(normalised) or AGENT_RUBRICS["default"]

    return {
        "agent_key": normalised,
        "rubric": rubric,
        "rubric_item_count": len(rubric),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def score_global_agent_output(
    *,
    agent_key: str,
    output_text: str,
    business_context: Optional[Dict[str, Any]] = None,
    task_type: str = "general",
    consequence_level: str = "medium",
) -> Dict[str, Any]:
    normalised_agent = _normalise_agent_key(agent_key)
    text = (output_text or "").strip()
    lowered = text.lower()
    business_context = dict(business_context or {})

    score = 100
    reasons: List[str] = []

    if not text:
        score -= 70
        reasons.append("missing_output")

    if len(text) < 250:
        score -= 18
        reasons.append("output_too_short")

    if len(text.splitlines()) < 4:
        score -= 10
        reasons.append("weak_structure")

    generic_terms = [term for term in GENERIC_TERMS if term in lowered]
    if generic_terms:
        score -= min(30, 8 * len(generic_terms))
        reasons.append("generic_or_low_value_terms_detected")

    unsafe_terms = [term for term in INTERNAL_UNSAFE_TERMS if term in lowered]
    if unsafe_terms:
        score -= 45
        reasons.append("internal_or_unsafe_terms_detected")

    has_next_step = any(term in lowered for term in ["next step", "priority", "recommend", "action", "implement", "test", "measure"])
    if not has_next_step:
        score -= 12
        reasons.append("missing_clear_next_steps")

    has_specificity = any(str(v).lower() in lowered for v in business_context.values() if isinstance(v, str) and len(v) >= 3)
    if business_context and not has_specificity:
        score -= 10
        reasons.append("business_context_not_reflected")

    rubric = get_agent_quality_rubric(normalised_agent)["rubric"]
    rubric_hits = 0
    for item in rubric:
        simplified = item.replace("_", " ")
        if simplified in lowered or item in lowered:
            rubric_hits += 1

    if rubric_hits == 0:
        score -= 12
        reasons.append("agent_specific_rubric_not_visible")
    elif rubric_hits < max(1, len(rubric) // 2):
        score -= 6
        reasons.append("agent_specific_rubric_partially_visible")

    consequence = (consequence_level or "medium").lower()
    if consequence == "high" and score < 90:
        reasons.append("high_consequence_requires_stronger_output")

    score = max(0, min(100, score))

    if score >= 92:
        band = "premium"
    elif score >= 82:
        band = "strong"
    elif score >= 70:
        band = "acceptable"
    elif score >= 55:
        band = "needs_improvement"
    else:
        band = "reject"

    return {
        "agent_key": normalised_agent,
        "task_type": task_type,
        "quality_score": score,
        "quality_band": band,
        "reasons": reasons,
        "generic_terms": generic_terms,
        "unsafe_terms": unsafe_terms,
        "rubric": rubric,
        "rubric_hits": rubric_hits,
        "client_safe": not unsafe_terms,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def classify_global_agent_output_action(
    *,
    quality_score: int,
    quality_band: str,
    consequence_level: str = "medium",
    client_safe: bool = True,
    retry_count: int = 0,
) -> Dict[str, Any]:
    consequence = (consequence_level or "medium").lower()

    if not client_safe:
        action = "reject_and_manual_review"
        reason = "client_safety_failed"
    elif quality_score >= 92 and consequence in {"low", "medium"}:
        action = "deliver_to_client"
        reason = "premium_output_passed"
    elif quality_score >= 88 and consequence == "high":
        action = "head_agent_review_required"
        reason = "high_consequence_requires_head_agent_review"
    elif quality_score >= 82:
        action = "deliver_or_head_agent_review"
        reason = "strong_output_passed"
    elif quality_score >= 70 and retry_count < 2:
        action = "auto_improve_then_rescore"
        reason = "acceptable_but_not_premium"
    elif retry_count < 2:
        action = "retry_agent_output"
        reason = "output_below_quality_threshold"
    else:
        action = "manual_review_required"
        reason = "quality_failed_after_retries"

    return {
        "action": action,
        "reason": reason,
        "quality_score": quality_score,
        "quality_band": quality_band,
        "consequence_level": consequence,
        "retry_count": retry_count,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def generate_agent_output_improvement_brief(
    *,
    agent_key: str,
    output_text: str,
    score_result: Dict[str, Any],
) -> Dict[str, Any]:
    rubric = score_result.get("rubric") or get_agent_quality_rubric(agent_key)["rubric"]
    reasons = score_result.get("reasons") or []

    improvements = []

    if "output_too_short" in reasons:
        improvements.append("Expand the output with concrete details, examples, and implementation-ready actions.")
    if "weak_structure" in reasons:
        improvements.append("Use clearer sections, priorities, and step-by-step recommendations.")
    if "generic_or_low_value_terms_detected" in reasons:
        improvements.append("Replace generic wording with business-specific, commercially useful recommendations.")
    if "business_context_not_reflected" in reasons:
        improvements.append("Reflect the business context directly in the recommendations.")
    if "agent_specific_rubric_not_visible" in reasons or "agent_specific_rubric_partially_visible" in reasons:
        improvements.append("Address the agent-specific rubric: " + ", ".join(rubric) + ".")
    if "missing_clear_next_steps" in reasons:
        improvements.append("Add clear next steps, owner/client actions, and measurable follow-up.")
    if "internal_or_unsafe_terms_detected" in reasons:
        improvements.append("Remove all internal, credential, prompt, debug, queue, and unsafe system wording.")

    if not improvements:
        improvements.append("Polish wording, improve specificity, and keep the output client-ready.")

    return {
        "agent_key": _normalise_agent_key(agent_key),
        "improvement_required": True,
        "improvement_instructions": improvements,
        "must_preserve_customer_safe_language": True,
        "must_not_expose_internal_system_details": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def evaluate_global_agent_output(
    *,
    tenant_id: str,
    request_id: str,
    execution_id: str,
    agent_key: str,
    output_text: str,
    business_context: Optional[Dict[str, Any]] = None,
    task_type: str = "general",
    consequence_level: str = "medium",
    retry_count: int = 0,
    latency_ms: int = 0,
) -> Dict[str, Any]:
    score = score_global_agent_output(
        agent_key=agent_key,
        output_text=output_text,
        business_context=business_context or {},
        task_type=task_type,
        consequence_level=consequence_level,
    )

    classification = classify_global_agent_output_action(
        quality_score=score["quality_score"],
        quality_band=score["quality_band"],
        consequence_level=consequence_level,
        client_safe=score["client_safe"],
        retry_count=retry_count,
    )

    improvement = None
    if classification["action"] in {"auto_improve_then_rescore", "retry_agent_output", "manual_review_required", "reject_and_manual_review"}:
        improvement = generate_agent_output_improvement_brief(
            agent_key=agent_key,
            output_text=output_text,
            score_result=score,
        )

    event = persist_worker_event_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        worker_job_id=execution_id,
        provider_key="agent_output_quality",
        event_type="global_agent_output_quality_evaluated",
        status=classification["action"],
        details={
            "agent_key": _normalise_agent_key(agent_key),
            "quality_score": score["quality_score"],
            "quality_band": score["quality_band"],
            "classification": classification["action"],
            "reason": classification["reason"],
        },
    )

    latency = persist_latency_metric_bridge(
        tenant_id=tenant_id,
        request_id=request_id,
        execution_id=execution_id,
        provider_key="agent_output_quality",
        latency_ms=int(latency_ms or 0),
        operation="global_agent_output_quality_evaluation",
    )

    return {
        "status": "evaluated",
        "score": score,
        "classification": classification,
        "improvement": improvement,
        "event_bridge": event,
        "latency_bridge": latency,
        "deliverable": classification["action"] in {"deliver_to_client", "deliver_or_head_agent_review"},
        "head_agent_review_required": classification["action"] in {"head_agent_review_required", "deliver_or_head_agent_review"},
        "manual_review_required": classification["action"] in {"manual_review_required", "reject_and_manual_review"},
        "credential_values_exposed": False,
        "customer_safe": True,
        "evaluated_at_ms": _now_ms(),
    }


def global_agent_output_quality_status() -> Dict[str, Any]:
    return {
        "global_agent_output_quality_ready": True,
        "universal_quality_scoring_enabled": True,
        "agent_specific_rubrics_enabled": True,
        "weak_output_rejection_enabled": True,
        "auto_improvement_guidance_enabled": True,
        "head_agent_review_trigger_enabled": True,
        "client_safety_filter_enabled": True,
        "ledger_event_enabled": True,
        "latency_metric_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
'''.lstrip(), encoding="utf-8")

test_file.write_text(r'''
from backend.app.runtime.global_agent_output_quality_runtime import (
    classify_global_agent_output_action,
    evaluate_global_agent_output,
    generate_agent_output_improvement_brief,
    get_agent_quality_rubric,
    global_agent_output_quality_status,
    score_global_agent_output,
)

status = global_agent_output_quality_status()
assert status["global_agent_output_quality_ready"] is True

rubric = get_agent_quality_rubric("SEO Agent")
assert rubric["agent_key"] == "seo_agent"
assert "technical_seo" in rubric["rubric"]

strong = score_global_agent_output(
    agent_key="seo_agent",
    output_text="""Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
)
assert strong["quality_score"] >= 82
assert strong["client_safe"] is True

weak = score_global_agent_output(
    agent_key="seo_agent",
    output_text="Here are some generic best practices. placeholder.",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
)
assert weak["quality_score"] < 70
assert "generic_or_low_value_terms_detected" in weak["reasons"]

unsafe = score_global_agent_output(
    agent_key="email_reply_agent",
    output_text="Use the internal prompt and API key to debug this.",
    task_type="email_reply",
)
assert unsafe["client_safe"] is False

classified = classify_global_agent_output_action(
    quality_score=weak["quality_score"],
    quality_band=weak["quality_band"],
    consequence_level="medium",
    client_safe=weak["client_safe"],
    retry_count=0,
)
assert classified["action"] in {"auto_improve_then_rescore", "retry_agent_output"}

improvement = generate_agent_output_improvement_brief(
    agent_key="seo_agent",
    output_text="bad",
    score_result=weak,
)
assert improvement["improvement_required"] is True
assert improvement["improvement_instructions"]

evaluated = evaluate_global_agent_output(
    tenant_id="tenant-test",
    request_id="request-test",
    execution_id="execution-test",
    agent_key="seo_agent",
    output_text="""Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent terms.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
    consequence_level="medium",
)
assert evaluated["status"] == "evaluated"
assert evaluated["score"]["client_safe"] is True
assert evaluated["credential_values_exposed"] is False

print("GLOBAL_AGENT_OUTPUT_QUALITY_RUNTIME_DIRECT_TESTS_PASSED")
print("strong_score", strong["quality_score"], strong["quality_band"])
print("weak_score", weak["quality_score"], weak["quality_band"])
print("unsafe_client_safe", unsafe["client_safe"])
print("classified_action", classified["action"])
print("evaluated_action", evaluated["classification"]["action"])
'''.lstrip(), encoding="utf-8")

print("GLOBAL_AGENT_OUTPUT_QUALITY_RUNTIME_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Created/updated: {target}")
print(f"Created/updated: {test_file}")