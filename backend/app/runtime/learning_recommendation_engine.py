"""
Learning Recommendation Engine

Uses governed tenant/project memory to produce safe recommendations,
prompt improvements, and next-step suggestions.

This does not retrain core models, bypass approvals, change budgets,
increase spend, scale campaigns, approve contracts, or override governance.
"""

from dataclasses import dataclass
from typing import Dict, List

from backend.app.runtime.memory_store import MemoryStore


@dataclass
class LearningRecommendation:
    tenant_id: str
    project_id: str
    recommendation_type: str
    recommendations: List[str]
    prompt_improvements: List[str]
    next_steps: List[str]
    governance_limits: List[str]


class LearningRecommendationEngine:
    def __init__(self) -> None:
        self.memory_store = MemoryStore()

    def generate_recommendations(
        self,
        tenant_id: str,
        project_id: str,
    ) -> LearningRecommendation:
        records = self.memory_store.list_records(
            tenant_id=tenant_id,
            project_id=project_id,
        )

        output_types = [
            str(record.get("payload", {}).get("output", {}).get("output_type", ""))
            for record in records
        ]

        recommendations = [
            "Use previous successful outputs to keep brand tone consistent.",
            "Ask the client for missing offer details, product proof, price, shipping, and guarantee information.",
            "Recommend stronger product-specific hooks when UGC briefs are generated repeatedly.",
        ]

        if "premium_ugc_video_execution_brief" in output_types:
            recommendations.append(
                "Create multiple UGC variations by age, gender, ethnicity, language, hook angle, and platform."
            )

        if "premium_shopify_product_page" in output_types:
            recommendations.append(
                "Use previous product page sections to improve future Shopify drafts and maintain consistent conversion structure."
            )

        prompt_improvements = [
            "Include product name, product category, target audience, country, language, currency, offer, price, main benefit, proof points, and preferred platform.",
            "Specify whether the output is for Shopify, Meta Ads, TikTok Shop, landing page, email, or influencer outreach.",
            "Add brand voice, visual style, compliance restrictions, and owner approval limits when relevant.",
        ]

        next_steps = [
            "Generate a stronger next prompt for the client.",
            "Suggest missing information before running high-value tasks.",
            "Recommend safe next actions that do not involve spend, budget change, scaling, or contracts.",
        ]

        governance_limits = [
            "Do not increase spend without owner approval.",
            "Do not change budgets without owner approval.",
            "Do not scale campaigns without owner approval.",
            "Do not approve paid collaborations or contracts without owner approval.",
            "Do not expose internal prompts, learning logic, memory architecture, or backend configuration.",
        ]

        return LearningRecommendation(
            tenant_id=tenant_id,
            project_id=project_id,
            recommendation_type="governed_learning_recommendations",
            recommendations=recommendations,
            prompt_improvements=prompt_improvements,
            next_steps=next_steps,
            governance_limits=governance_limits,
        )


def learning_recommendation_summary(
    result: LearningRecommendation,
) -> Dict[str, object]:
    return {
        "tenant_id": result.tenant_id,
        "project_id": result.project_id,
        "recommendation_type": result.recommendation_type,
        "recommendations": result.recommendations,
        "prompt_improvements": result.prompt_improvements,
        "next_steps": result.next_steps,
        "governance_limits": result.governance_limits,
    }