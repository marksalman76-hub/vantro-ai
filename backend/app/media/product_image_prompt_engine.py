"""
Product Image Prompt Engine

Builds premium, realistic, globally adaptable product image production briefs.
Designed for ecommerce stores, ads, landing pages, UGC-style images, and
white-label client delivery.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ProductImagePromptRequest:
    product_name: str
    product_category: str
    target_audience: str
    region: str
    language: str
    currency: str
    brand_style: str
    image_type: str
    platform: str
    scene_direction: str


class ProductImagePromptEngine:
    def build_prompt(self, request: ProductImagePromptRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "premium_product_image_production_brief",
            "quality_tier": "premium_commercial_ad_ready",
            "benchmark_standard": "exceed_high_quality_ai_product_photography_and_ad_creative_tools",
            "product_name": request.product_name,
            "product_category": request.product_category,
            "target_audience": request.target_audience,
            "region": request.region,
            "language": request.language,
            "currency": request.currency,
            "brand_style": request.brand_style,
            "image_type": request.image_type,
            "platform": request.platform,
            "scene_direction": request.scene_direction,
            "production_brief": (
                f"Create a premium, realistic, commercially usable {request.image_type} image "
                f"for {request.product_name}, a {request.product_category} product. "
                f"The image must suit {request.platform}, feel native to {request.region}, "
                f"and appeal to {request.target_audience}. The visual style should be "
                f"{request.brand_style}. Scene direction: {request.scene_direction}. "
                f"The final image must look ecommerce-ready, advertising-ready, realistic, "
                f"brand-safe, polished, and commercially believable. Preserve the product shape, "
                f"label logic, packaging proportions, material texture, scale, and product category accuracy."
            ),
            "image_format_requirements": {
                "shopify_product_page": [
                    "Clean product hero image",
                    "Feature-detail image",
                    "Lifestyle usage image",
                    "Mobile-friendly crop",
                ],
                "paid_ads": [
                    "Strong first-glance clarity",
                    "Platform-native composition",
                    "High contrast product visibility",
                    "Clear benefit cue",
                ],
                "landing_page": [
                    "Hero image option",
                    "Trust-building lifestyle image",
                    "Offer-supporting visual",
                    "Section background option",
                ],
                "ugc_style": [
                    "Realistic creator-held product image",
                    "Natural lighting",
                    "Authentic environment",
                    "No staged stock-photo look",
                ],
            },
            "composition_requirements": [
                "Clear product visibility",
                "Premium lighting",
                "Realistic scale and proportions",
                "Brand-consistent colour palette",
                "Clean ecommerce composition",
                "Strong first-glance clarity",
                "Mobile-friendly framing",
                "Ad-platform-ready layout",
                "Product remains the hero of the image",
                "Background supports but does not overpower the product",
            ],
            "realism_requirements": [
                "Realistic shadows",
                "Realistic reflections",
                "Natural lighting direction",
                "Accurate material texture",
                "Correct product geometry",
                "Believable environment",
                "Culturally suitable styling for the target region",
                "No impossible object placement",
            ],
            "product_accuracy_controls": [
                "Preserve product shape",
                "Preserve packaging proportions",
                "Do not invent unreadable labels",
                "Do not change product category",
                "Do not add misleading claims",
                "Do not create impossible before/after effects",
                "Avoid fake certification badges unless provided",
            ],
            "quality_rejection_rules": [
                "Reject distorted product shape",
                "Reject incorrect labels",
                "Reject unrealistic reflections",
                "Reject bad hands",
                "Reject strange body positioning",
                "Reject low-resolution artefacts",
                "Reject generic stock-photo look",
                "Reject off-brand background",
                "Reject unreadable text",
                "Reject misleading product representation",
                "Reject culturally inappropriate styling",
                "Reject images unsuitable for paid advertising",
            ],
            "image_variations": [
                "Studio hero image",
                "Lifestyle usage image",
                "UGC-style social image",
                "Feature-benefit image",
                "Before/after concept",
                "Ad creative image",
                "Landing page hero image",
                "Marketplace thumbnail",
                "Premium bundle image",
                "Region-localised lifestyle image",
            ],
            "approval_rules": {
                "automatic_allowed": [
                    "Image brief generation",
                    "Product scene direction",
                    "Ad image concept generation",
                    "Store image direction",
                    "Lifestyle image direction",
                    "UGC-style image direction",
                    "Image quality checklist generation",
                ],
                "owner_approval_required": [
                    "Paid media spend",
                    "Paid creator shoot",
                    "Licensed model agreement",
                    "Usage-rights contract",
                    "Campaign scaling",
                    "Large budget commitment",
                ],
            },
        }


def product_image_prompt_summary(prompt: Dict[str, object]) -> Dict[str, object]:
    return {
        "client_safe": prompt.get("client_safe"),
        "output_type": prompt.get("output_type"),
        "quality_tier": prompt.get("quality_tier"),
        "benchmark_standard": prompt.get("benchmark_standard"),
        "product_name": prompt.get("product_name"),
        "image_type": prompt.get("image_type"),
        "platform": prompt.get("platform"),
        "region": prompt.get("region"),
        "brand_style": prompt.get("brand_style"),
        "composition_requirements": prompt.get("composition_requirements"),
        "realism_requirements": prompt.get("realism_requirements"),
        "product_accuracy_controls": prompt.get("product_accuracy_controls"),
        "quality_rejection_rules": prompt.get("quality_rejection_rules"),
        "approval_rules": prompt.get("approval_rules"),
    }