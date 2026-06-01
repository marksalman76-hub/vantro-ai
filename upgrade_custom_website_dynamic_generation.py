from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "custom_website_generation_runtime.py"
BACKUP = ROOT / "backups" / f"custom_website_dynamic_generation_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "custom_website_generation_runtime.py")

s = TARGET.read_text(encoding="utf-8")

s = s.replace(
'''    headline = "Clinical Radiance, Reimagined as Luxury Ritual"
    subheadline = strategy["subheadline"]''',
'''    headline = strategy["headline"]
    subheadline = strategy["subheadline"]'''
)

s = s.replace(
'''            "sections": ["sticky nav", "hero", "benefits", "ritual architecture", "offer", "proof", "faq", "sticky cta"],''',
'''            "sections": ["sticky nav", "hero", "benefits", "product/service architecture", "offer", "proof", "faq", "sticky cta"],'''
)

s = s.replace(
'''    if "skincare" in lower:
        return "Aurelise"
    if "fitness" in lower:
        return "PeakForm"
    if "real estate" in lower:
        return "PrimeNest"
    if "restaurant" in lower or "cafe" in lower:
        return "Maison Table"
    return "Premium Brand"''',
'''    if "skincare" in lower:
        return "Aurelise"
    if "fitness" in lower or "gym" in lower:
        return "PeakForm"
    if "real estate" in lower or "property" in lower:
        return "PrimeNest"
    if "restaurant" in lower or "cafe" in lower:
        return "Maison Table"
    if "law" in lower or "legal" in lower:
        return "Lexora"
    if "coach" in lower or "consulting" in lower or "consultant" in lower:
        return "Advisora"
    if "saas" in lower or "software" in lower or "platform" in lower:
        return "Nexora"
    return "Premium Brand"'''
)

s = s.replace(
'''    return {
        "industry": "premium ecommerce",
        "audience": "high-intent premium buyers",
        "headline": "A Premium Digital Experience Built to Convert",
        "subheadline": "A custom generated landing page with conversion structure, brand positioning, offer architecture, and publish-ready draft assets.",
        "primary_cta": "Start Now",
        "secondary_cta": "View Details",
        "offer": "Launch offer prepared for conversion testing.",
        "product": "Premium Offer",
        "proof": ["Premium positioning", "Conversion hierarchy", "Trust framework", "Responsive layout"],
        "keywords": ["premium ecommerce", "conversion landing page"],
    }''',
'''    if "fitness" in lower or "gym" in lower:
        return {
            "industry": "fitness",
            "audience": "health-conscious local members",
            "headline": "Train Smarter, Feel Stronger, Stay Consistent",
            "subheadline": "A premium fitness landing page designed to turn motivated visitors into trial bookings, memberships, and long-term clients.",
            "primary_cta": "Book a Trial Session",
            "secondary_cta": "View Programs",
            "offer": "Intro offer: 7-day trial pass with personalised onboarding and goal-setting session.",
            "product": "Performance Program",
            "proof": ["Personalised onboarding", "Strength and conditioning", "Flexible membership paths", "Progress-focused coaching"],
            "keywords": ["fitness programs", "local gym", "personal training"],
        }

    if "real estate" in lower or "property" in lower:
        return {
            "industry": "real estate",
            "audience": "premium property buyers and sellers",
            "headline": "Premium Property Campaigns Built to Win Attention",
            "subheadline": "A custom real-estate landing page for showcasing high-value listings, buyer confidence, and agent authority.",
            "primary_cta": "Book an Appraisal",
            "secondary_cta": "View Listings",
            "offer": "Campaign-ready property page with valuation CTA, listing highlights, suburb proof, and enquiry capture.",
            "product": "Property Campaign",
            "proof": ["Suburb expertise", "Buyer enquiry capture", "Premium listing presentation", "Appraisal conversion flow"],
            "keywords": ["real estate agent", "property appraisal", "premium listings"],
        }

    if "restaurant" in lower or "cafe" in lower:
        return {
            "industry": "hospitality",
            "audience": "local diners and event guests",
            "headline": "A Dining Experience Worth Booking Tonight",
            "subheadline": "A premium hospitality landing page built to convert visitors into bookings, takeaway orders, and repeat customers.",
            "primary_cta": "Book a Table",
            "secondary_cta": "View Menu",
            "offer": "Launch dining offer with menu highlights, signature dishes, booking CTA, and social proof.",
            "product": "Signature Dining Experience",
            "proof": ["Chef-led menu", "Local favourite positioning", "Booking-first layout", "Event and group dining CTA"],
            "keywords": ["restaurant booking", "local dining", "premium cafe"],
        }

    if "law" in lower or "legal" in lower:
        return {
            "industry": "legal services",
            "audience": "clients seeking trusted legal guidance",
            "headline": "Clear Legal Guidance When the Stakes Matter",
            "subheadline": "A professional legal landing page designed to build trust, explain services, and convert urgent enquiries.",
            "primary_cta": "Request a Consultation",
            "secondary_cta": "View Services",
            "offer": "Consultation-ready legal page with trust signals, service breakdown, and enquiry flow.",
            "product": "Legal Consultation",
            "proof": ["Confidential enquiry flow", "Service clarity", "Trust-led design", "Consultation CTA"],
            "keywords": ["legal consultation", "law firm", "trusted legal advice"],
        }

    if "saas" in lower or "software" in lower or "platform" in lower:
        return {
            "industry": "software",
            "audience": "operators and business decision-makers",
            "headline": "A Smarter Platform Experience Built for Scale",
            "subheadline": "A premium SaaS landing page structured around product value, workflow clarity, proof, and demo conversion.",
            "primary_cta": "Book a Demo",
            "secondary_cta": "Explore Features",
            "offer": "Demo-ready SaaS page with feature blocks, value proposition, proof, and activation CTA.",
            "product": "Software Platform",
            "proof": ["Workflow automation", "Scalable operations", "Security-ready positioning", "Demo conversion flow"],
            "keywords": ["business software", "automation platform", "SaaS demo"],
        }

    return {
        "industry": "premium service",
        "audience": "high-intent premium buyers",
        "headline": "A Premium Digital Experience Built to Convert",
        "subheadline": "A custom generated landing page with conversion structure, brand positioning, offer architecture, and publish-ready draft assets.",
        "primary_cta": "Start Now",
        "secondary_cta": "View Details",
        "offer": "Launch offer prepared for conversion testing.",
        "product": "Premium Offer",
        "proof": ["Premium positioning", "Conversion hierarchy", "Trust framework", "Responsive layout"],
        "keywords": ["premium service", "conversion landing page"],
    }'''
)

s = s.replace("The ritual architecture", "The conversion architecture")
s = s.replace("Begin the radiance ritual with an exclusive launch bundle", "__OFFER_HEADLINE__")
s = s.replace("Radiance Renewal System", "__PRODUCT__")
s = s.replace("Hydration-led ritual", "Value-led experience")
s = s.replace("Built for glow, trust, and premium daily use.", "Built for trust, clarity, and premium conversion.")
s = s.replace("Luxury skincare visual direction", "Premium brand visual direction")
s = s.replace("Visible Glow Positioning", "Premium Positioning")
s = s.replace("Copy framework built around hydration, radiance, and skin confidence.", "Copy framework built around clarity, value, trust, and conversion.")
s = s.replace("Luxury Ritual Story", "Brand Story")
s = s.replace("Editorial-style brand language designed to feel premium, not generic.", "Industry-specific brand language designed to feel premium, not generic.")

s = s.replace(
'''        "__OFFER__": strategy["offer"],''',
'''        "__OFFER__": strategy["offer"],
        "__OFFER_HEADLINE__": f"Launch {strategy['product']} with a premium conversion experience",'''
)

TARGET.write_text(s, encoding="utf-8")
print("CUSTOM_WEBSITE_DYNAMIC_GENERATION_UPGRADED")
print("Backup:", BACKUP)