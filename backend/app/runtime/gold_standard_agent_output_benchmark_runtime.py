from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from backend.app.runtime.global_agent_output_quality_runtime import (
    evaluate_global_agent_output,
    get_agent_quality_rubric,
)


GOLD_STANDARD_BENCHMARKS = {
    "seo_agent": [
        {
            "benchmark_id": "seo_gold_1",
            "must_include": ["technical seo", "local seo", "keywords", "priority actions", "measurement"],
            "quality_traits": ["specific", "ranked priorities", "client-ready", "commercial intent"],
        }
    ],
    "marketing_specialist_agent": [
        {
            "benchmark_id": "marketing_gold_1",
            "must_include": ["audience", "offer", "positioning", "cta", "campaign actions"],
            "quality_traits": ["conversion-focused", "brand-aware", "actionable", "measurable"],
        }
    ],
    "lead_generator_agent": [
        {
            "benchmark_id": "leadgen_gold_1",
            "must_include": ["ideal customer", "personalisation", "outreach", "follow-up", "qualification"],
            "quality_traits": ["specific ICP", "conversion-focused", "low-risk", "actionable"],
        }
    ],
    "website_agent": [
        {
            "benchmark_id": "website_gold_1",
            "must_include": ["hero", "sections", "conversion", "ux", "implementation"],
            "quality_traits": ["premium layout", "clear structure", "conversion-ready", "brand-fit"],
        }
    ],
    "head_agent": [
        {
            "benchmark_id": "head_gold_1",
            "must_include": ["summary", "priority", "risk", "recommendation", "next step"],
            "quality_traits": ["executive-level", "decisive", "risk-aware", "commercially useful"],
        }
    ],
    "default": [
        {
            "benchmark_id": "default_gold_1",
            "must_include": ["specific recommendation", "commercial value", "next step", "measurement"],
            "quality_traits": ["specific", "client-ready", "actionable", "safe"],
        }
    ],
}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _normalise_agent_key(agent_key: str) -> str:
    return (agent_key or "default").strip().lower().replace(" ", "_").replace("-", "_")


def get_gold_standard_benchmark(agent_key: str) -> Dict[str, Any]:
    key = _normalise_agent_key(agent_key)
    benchmarks = GOLD_STANDARD_BENCHMARKS.get(key) or GOLD_STANDARD_BENCHMARKS["default"]

    return {
        "agent_key": key,
        "benchmarks": benchmarks,
        "benchmark_count": len(benchmarks),
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def score_output_against_gold_standard(
    *,
    agent_key: str,
    output_text: str,
    business_context: Optional[Dict[str, Any]] = None,
    task_type: str = "general",
    consequence_level: str = "medium",
) -> Dict[str, Any]:
    key = _normalise_agent_key(agent_key)
    text = (output_text or "").lower()
    benchmark_pack = get_gold_standard_benchmark(key)
    benchmark = benchmark_pack["benchmarks"][0]
    rubric = get_agent_quality_rubric(key)["rubric"]

    must_include = benchmark["must_include"]
    quality_traits = benchmark["quality_traits"]

    included = [item for item in must_include if item.lower() in text]
    missing = [item for item in must_include if item.lower() not in text]

    trait_hits = [trait for trait in quality_traits if trait.lower() in text]
    rubric_hits = [item for item in rubric if item.replace("_", " ").lower() in text or item.lower() in text]

    base_quality = evaluate_global_agent_output(
        tenant_id="benchmark-tenant",
        request_id="benchmark-request",
        execution_id="benchmark-execution",
        agent_key=key,
        output_text=output_text,
        business_context=business_context or {},
        task_type=task_type,
        consequence_level=consequence_level,
    )

    score = int(base_quality["score"]["quality_score"])

    if missing:
        score -= min(20, len(missing) * 5)
    if len(trait_hits) < 2:
        score -= 4
    if len(rubric_hits) < max(1, len(rubric) // 2):
        score -= 4

    score = max(0, min(100, score))

    if score >= 92:
        benchmark_band = "gold_standard"
    elif score >= 84:
        benchmark_band = "near_gold"
    elif score >= 72:
        benchmark_band = "acceptable_but_improvable"
    else:
        benchmark_band = "below_benchmark"

    improvement_required = score < 84

    return {
        "agent_key": key,
        "benchmark_id": benchmark["benchmark_id"],
        "benchmark_score": score,
        "benchmark_band": benchmark_band,
        "must_include_present": included,
        "must_include_missing": missing,
        "quality_trait_hits": trait_hits,
        "rubric_hits": rubric_hits,
        "base_quality_score": (
            base_quality.get("score", {}).get("quality_score", 0)
        ),
        "base_delivery_status": (
            base_quality.get("delivery_status")
            or base_quality.get("classified_action")
            or base_quality.get("delivery_action")
            or "unknown"
        ),
        "improvement_required": improvement_required,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def generate_benchmark_improvement_plan(
    *,
    agent_key: str,
    benchmark_score: Dict[str, Any],
) -> Dict[str, Any]:
    missing = benchmark_score.get("must_include_missing") or []
    band = benchmark_score.get("benchmark_band")

    instructions = []

    if missing:
        instructions.append("Add missing gold-standard elements: " + ", ".join(missing) + ".")

    if band in {"below_benchmark", "acceptable_but_improvable"}:
        instructions.append("Increase commercial specificity, client-ready structure, and implementation detail.")

    if len(benchmark_score.get("quality_trait_hits") or []) < 2:
        instructions.append("Make the output more benchmark-aligned by adding stronger commercial, strategic, and actionable traits.")

    if not instructions:
        instructions.append("Polish wording and preserve the current benchmark-level quality.")

    return {
        "agent_key": _normalise_agent_key(agent_key),
        "improvement_required": benchmark_score.get("improvement_required", False),
        "benchmark_band": band,
        "instructions": instructions,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def evaluate_output_against_gold_standard(
    *,
    agent_key: str,
    output_text: str,
    business_context: Optional[Dict[str, Any]] = None,
    task_type: str = "general",
    consequence_level: str = "medium",
) -> Dict[str, Any]:
    score = score_output_against_gold_standard(
        agent_key=agent_key,
        output_text=output_text,
        business_context=business_context or {},
        task_type=task_type,
        consequence_level=consequence_level,
    )

    plan = generate_benchmark_improvement_plan(
        agent_key=agent_key,
        benchmark_score=score,
    )

    delivery_allowed = score["benchmark_score"] >= 84 and not score["must_include_missing"]

    return {
        "status": "benchmark_evaluated",
        "score": score,
        "improvement_plan": plan,
        "delivery_allowed_by_benchmark": delivery_allowed,
        "head_agent_review_recommended": score["benchmark_score"] < 92,
        "credential_values_exposed": False,
        "customer_safe": True,
        "evaluated_at_ms": _now_ms(),
    }


def gold_standard_agent_output_benchmark_status() -> Dict[str, Any]:
    return {
        "gold_standard_benchmark_ready": True,
        "benchmark_agent_count": len(GOLD_STANDARD_BENCHMARKS),
        "benchmark_scoring_enabled": True,
        "must_include_checks_enabled": True,
        "quality_trait_checks_enabled": True,
        "benchmark_improvement_plan_enabled": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
