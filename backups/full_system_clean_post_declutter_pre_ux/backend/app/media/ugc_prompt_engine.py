"""
UGC Prompt Engine

Builds premium, realistic, globally adaptable UGC production briefs.
Designed for white-label ecommerce use with premium audio/video standards
and future real-world provider execution support.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class UGCPromptRequest:
    product_name: str
    product_category: str
    target_audience: str
    region: str
    language: str
    currency: str
    creator_age_range: str
    creator_gender: str
    creator_ethnicity: str
    creator_accent: str
    platform: str
    tone: str


class UGCPromptEngine:
    def build_prompt(self, request: UGCPromptRequest) -> Dict[str, object]:
        return {
            "client_safe": True,
            "output_type": "realistic_ugc_production_brief",
            "quality_tier": "premium_commercial_ad_ready",
            "benchmark_standard": "exceed_high_quality_ai_video_audio_and_creator_content_tools",
            "provider_execution_ready": True,
            "product_name": request.product_name,
            "product_category": request.product_category,
            "target_audience": request.target_audience,
            "platform": request.platform,
            "region": request.region,
            "language": request.language,
            "currency": request.currency,
            "creator_profile": {
                "age_range": request.creator_age_range,
                "gender": request.creator_gender,
                "ethnicity": request.creator_ethnicity,
                "accent": request.creator_accent,
                "tone": request.tone,
                "delivery_style": "natural, believable, platform-native",
            },
            "production_brief": (
                f"Create a premium, realistic, commercially usable {request.platform} UGC video "
                f"for {request.product_name}, a {request.product_category} product. "
                f"The creator should match this profile: {request.creator_age_range}, "
                f"{request.creator_gender}, {request.creator_ethnicity}, speaking {request.language} "
                f"with a {request.creator_accent} accent. The content must feel native to "
                f"{request.region}, culturally appropriate, brand-safe, commercially believable, "
                f"and relevant to {request.target_audience}. The delivery should be {request.tone}, "
                f"natural, emotionally believable, conversational, and not over-scripted."
            ),
            "shot_plan": [
                {
                    "scene": 1,
                    "timing": "0-3s",
                    "purpose": "Scroll-stopping hook",
                    "direction": "Immediate audience pain point or curiosity trigger.",
                },
                {
                    "scene": 2,
                    "timing": "3-8s",
                    "purpose": "Relatable emotional moment",
                    "direction": "Show realistic lifestyle problem or desire.",
                },
                {
                    "scene": 3,
                    "timing": "8-16s",
                    "purpose": "Product introduction",
                    "direction": "Natural creator-led product demonstration.",
                },
                {
                    "scene": 4,
                    "timing": "16-25s",
                    "purpose": "Benefit proof",
                    "direction": "Demonstrate believable product value or transformation.",
                },
                {
                    "scene": 5,
                    "timing": "25-35s",
                    "purpose": "Trust and objection handling",
                    "direction": "Reduce buyer hesitation naturally.",
                },
                {
                    "scene": 6,
                    "timing": "35-45s",
                    "purpose": "Soft CTA",
                    "direction": "Encourage action without aggressive selling.",
                },
            ],
            "audio_quality_requirements": [
                "Natural human speech rhythm",
                "Native or region-appropriate pronunciation",
                "No robotic cadence",
                "No audio lag",
                "No clipped words",
                "No unnatural pauses",
                "Clear commercial-quality voice output",
                "Emotionally believable delivery",
                "Platform-native pacing",
            ],
            "video_quality_requirements": [
                "Accurate lip sync",
                "Smooth facial movement",
                "Realistic expressions",
                "Realistic hand movement",
                "No distorted face",
                "No distorted hands",
                "No flickering",
                "No warping",
                "No uncanny facial behaviour",
                "No lag between audio and mouth movement",
                "Commercial-ad-ready output",
                "Mobile-first framing",
            ],
            "provider_execution_packet": {
                "provider_flexible": True,
                "supported_provider_categories": [
                    "avatar_video_generation",
                    "ugc_creator_generation",
                    "voice_generation",
                    "video_rendering",
                ],
                "required_runtime_fields": [
                    "creator_profile",
                    "language",
                    "accent",
                    "platform",
                    "scene_direction",
                    "audio_quality_requirements",
                    "video_quality_requirements",
                ],
            },
            "quality_rejection_rules": [
                "Reject robotic speech",
                "Reject weak lip sync",
                "Reject distorted face",
                "Reject distorted hands",
                "Reject lag between speech and mouth movement",
                "Reject emotionless delivery",
                "Reject uncanny facial movement",
                "Reject unrealistic body movement",
                "Reject low-resolution output",
                "Reject culturally inappropriate styling",
                "Reject non-platform-native pacing",
            ],
            "variation_requirements": [
                "Generate multiple hook options",
                "Support different creator age ranges",
                "Support different genders",
                "Support different ethnicities",
                "Support different accents",
                "Support multilingual delivery",
                "Support region-specific buyer psychology",
                "Support platform-specific pacing and style",
            ],
            "approval_rules": {
                "automatic_allowed": [
                    "UGC script generation",
                    "Creator profile direction",
                    "Shot list generation",
                    "Video brief generation",
                    "Language and accent variation planning",
                    "UGC execution packet preparation",
                ],
                "owner_approval_required": [
                    "Paid creator collaboration",
                    "Usage-rights agreement",
                    "Product seeding at scale",
                    "Budget commitment",
                    "Campaign spend increase",
                    "Campaign scaling",
                ],
            },
        }


def ugc_prompt_summary(prompt: Dict[str, object]) -> Dict[str, object]:
    return {
        "client_safe": prompt.get("client_safe"),
        "output_type": prompt.get("output_type"),
        "quality_tier": prompt.get("quality_tier"),
        "provider_execution_ready": prompt.get("provider_execution_ready"),
        "product_name": prompt.get("product_name"),
        "platform": prompt.get("platform"),
        "region": prompt.get("region"),
        "language": prompt.get("language"),
        "creator_profile": prompt.get("creator_profile"),
        "audio_quality_requirements": prompt.get("audio_quality_requirements"),
        "video_quality_requirements": prompt.get("video_quality_requirements"),
        "quality_rejection_rules": prompt.get("quality_rejection_rules"),
        "approval_rules": prompt.get("approval_rules"),
    }