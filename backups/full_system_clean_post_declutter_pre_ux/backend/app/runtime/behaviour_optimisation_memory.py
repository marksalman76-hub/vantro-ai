"""
Behaviour Optimisation Memory

Creates governed optimisation signals from tenant/project execution history.

This layer helps agents improve recommendations, prompts, and workflow choices
over time without bypassing approvals or changing budgets/spend/contracts.
"""

from dataclasses import dataclass
from typing import Dict, List

from backend.app.runtime.memory_store import MemoryStore


@dataclass
class BehaviourOptimisationReport:
    tenant_id: str
    project_id: str
    optimisation_type: str
    observed_patterns: List[str]
    improvement_opportunities: List[str]
    recommended_prompt_additions: List[str]
    safe_action_recommendations: List[str]
    blocked_autonomous_actions: List[str]


class BehaviourOptimisationMemory:
    def __init__(self) -> None:
        self.memory_store = MemoryStore()

    def analyse_project(
        self,
        tenant_id: str,
        project_id: str,
    ) -> BehaviourOptimisationReport:
        records = self.memory_store.list_records(
            tenant_id=tenant_id,
            project_id=project_id,
        )

        output_types = [
            str(record.get("payload", {}).get("output", {}).get("output_type", ""))
            for record in records
        ]

        observed_patterns = [
            f"Total remembered project records: {len(records)}",
            "Successful outputs are available for future prompt and recommendation improvement."
            if records
            else "No project execution history is available yet.",
        ]

        if "premium_ugc_video_execution_brief" in output_types:
            observed_patterns.append(
                "UGC execution briefs are being generated for this project."
            )

        if "premium_product_image_direction" in output_types:
            observed_patterns.append(
                "Product image direction outputs are being generated for this project."
            )

        if "premium_shopify_product_page" in output_types:
            observed_patterns.append(
                "Shopify product page outputs are being generated for this project."
            )

        improvement_opportunities = [
            "Request more product proof points before generating final client-facing copy.",
            "Collect preferred brand voice and visual direction for better consistency.",
            "Ask for offer details, price, shipping terms, guarantee, and primary objection.",
            "Use previous successful structures to improve future outputs for this tenant.",
        ]

        recommended_prompt_additions = [
            "Product name",
            "Product category",
            "Target audience",
            "Country/region",
            "Language",
            "Currency",
            "Offer",
            "Price",
            "Main product benefit",
            "Proof points",
            "Brand voice",
            "Platform",
            "Visual style",
            "Compliance restrictions",
        ]

        safe_action_recommendations = [
            "Generate improved prompt suggestions for the client.",
            "Create additional UGC hook variations.",
            "Prepare image direction variations.",
            "Prepare Shopify draft page improvements.",
            "Recommend missing inputs before execution.",
        ]

        blocked_autonomous_actions = [
            "Increase spend",
            "Change campaign budget",
            "Scale campaign",
            "Launch paid ads",
            "Approve paid influencer collaboration",
            "Sign usage-rights agreement",
            "Override tenant/package access",
            "Expose internal learning architecture",
        ]

        return BehaviourOptimisationReport(
            tenant_id=tenant_id,
            project_id=project_id,
            optimisation_type="governed_behaviour_optimisation",
            observed_patterns=observed_patterns,
            improvement_opportunities=improvement_opportunities,
            recommended_prompt_additions=recommended_prompt_additions,
            safe_action_recommendations=safe_action_recommendations,
            blocked_autonomous_actions=blocked_autonomous_actions,
        )


def behaviour_optimisation_summary(
    report: BehaviourOptimisationReport,
) -> Dict[str, object]:
    return {
        "tenant_id": report.tenant_id,
        "project_id": report.project_id,
        "optimisation_type": report.optimisation_type,
        "observed_patterns": report.observed_patterns,
        "improvement_opportunities": report.improvement_opportunities,
        "recommended_prompt_additions": report.recommended_prompt_additions,
        "safe_action_recommendations": report.safe_action_recommendations,
        "blocked_autonomous_actions": report.blocked_autonomous_actions,
    }