"""
Ecommerce Copy Engine

Builds premium, conversion-focused ecommerce copy briefs for product pages,
landing pages, ads, email, and white-label client delivery.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class EcommerceCopyRequest:
    product_name: str
    product_category: str
    target_audience: str
    region: str
    language: str
    currency: str
    brand_voice: str
    offer: str
    page_type: str
    main_pain_point: str
    main_benefit: str


class EcommerceCopyEngine:
    def build_copy_brief(self, request: EcommerceCopyRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "premium_ecommerce_copy_brief",
            "quality_tier": "premium_conversion_ready",
            "product_name": request.product_name,
            "product_category": request.product_category,
            "target_audience": request.target_audience,
            "region": request.region,
            "language": request.language,
            "currency": request.currency,
            "brand_voice": request.brand_voice,
            "page_type": request.page_type,
            "copy_brief": (
                f"Create premium, conversion-focused {request.page_type} copy for "
                f"{request.product_name}, a {request.product_category} product. "
                f"The copy must be written in {request.language}, adapted for {request.region}, "
                f"priced and positioned around {request.currency}, and written in a "
                f"{request.brand_voice} voice. The offer is: {request.offer}. "
                f"The main pain point is: {request.main_pain_point}. "
                f"The main benefit is: {request.main_benefit}. "
                f"The copy must be commercially usable, emotionally persuasive, trust-building, "
                f"benefit-led, objection-aware, and suitable for white-label client delivery."
            ),
            "required_sections": [
                "Benefit-led headline",
                "Emotional opening hook",
                "Problem amplification",
                "Product solution positioning",
                "Feature-to-benefit bullets",
                "Trust and credibility section",
                "Objection handling",
                "Offer and value framing",
                "FAQ section",
                "Strong call-to-action",
            ],
            "conversion_requirements": [
                "Lead with benefits before features",
                "Use clear buyer psychology",
                "Match local market expectations",
                "Avoid generic AI wording",
                "Create urgency without false scarcity",
                "Use simple and persuasive language",
                "Make the offer easy to understand",
                "Build trust before asking for action",
            ],
            "quality_rejection_rules": [
                "Reject generic copy",
                "Reject robotic wording",
                "Reject unclear offer positioning",
                "Reject weak headline",
                "Reject unsupported claims",
                "Reject misleading urgency",
                "Reject off-brand tone",
                "Reject copy that is not client-ready",
            ],
            "approval_rules": {
                "automatic_allowed": [
                    "Product page copy generation",
                    "Landing page copy generation",
                    "Ad copy generation",
                    "Email copy generation",
                    "SEO metadata generation",
                    "Offer copy drafting",
                ],
                "owner_approval_required": [
                    "Major pricing strategy change",
                    "Campaign budget change",
                    "Paid campaign launch",
                    "Campaign scaling",
                    "Contractual claim or guarantee change",
                ],
            },
        }


def ecommerce_copy_summary(copy_brief: Dict[str, object]) -> Dict[str, object]:
    return {
        "client_safe": copy_brief.get("client_safe"),
        "output_type": copy_brief.get("output_type"),
        "quality_tier": copy_brief.get("quality_tier"),
        "product_name": copy_brief.get("product_name"),
        "page_type": copy_brief.get("page_type"),
        "region": copy_brief.get("region"),
        "language": copy_brief.get("language"),
        "required_sections": copy_brief.get("required_sections"),
        "conversion_requirements": copy_brief.get("conversion_requirements"),
        "approval_rules": copy_brief.get("approval_rules"),
    }