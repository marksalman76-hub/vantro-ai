from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

pack = {
    "step": 119,
    "name": "Domain/DNS Production Configuration Pack",
    "generated_at_utc": now,
    "status": "domain_dns_production_config_pack_created",
    "secret_values_included": False,
    "domain_dns_requirements": {
        "recommended_dns_providers": [
            "Cloudflare",
            "GoDaddy",
            "Namecheap",
            "Squarespace Domains",
            "Route 53"
        ],
        "required_domains": [
            "frontend production domain",
            "backend/API production domain or provider URL"
        ],
        "required_dns_records": [
            "frontend host DNS record",
            "backend/API DNS record if custom API domain is used",
            "email SPF record if email sending is enabled",
            "email DKIM record if email sending is enabled",
            "DMARC record recommended"
        ],
        "required_controls": [
            "HTTPS/TLS enabled",
            "www/non-www redirect decision made",
            "frontend domain added to backend CORS allowlist",
            "backend API URL configured in frontend host",
            "no mixed-content browser errors",
            "admin route accessible only under intended production domain",
            "client route accessible under intended production domain"
        ],
        "required_validation": [
            "frontend URL loads over HTTPS",
            "backend health endpoint responds over HTTPS",
            "admin page route resolves",
            "client page route resolves",
            "frontend can reach backend API without CORS error",
            "DNS propagation confirmed",
            "email DNS records confirmed if email is enabled"
        ],
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "cors_security_production_config_pack",
    },
}

json_path = DATA / "step119_domain_dns_production_config_pack.json"
md_path = DOCS / "STEP_119_DOMAIN_DNS_PRODUCTION_CONFIG_PACK.md"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

providers = "\n".join(f"- {item}" for item in pack["domain_dns_requirements"]["recommended_dns_providers"])
domains = "\n".join(f"- {item}" for item in pack["domain_dns_requirements"]["required_domains"])
records = "\n".join(f"- {item}" for item in pack["domain_dns_requirements"]["required_dns_records"])
controls = "\n".join(f"- {item}" for item in pack["domain_dns_requirements"]["required_controls"])
validation = "\n".join(f"- {item}" for item in pack["domain_dns_requirements"]["required_validation"])

md = f"""# Step 119 — Domain/DNS Production Configuration Pack

Generated: {now}

## Status

**Result:** Domain/DNS production configuration pack created.  
**Secret values included:** No

## Recommended DNS Providers

{providers}

## Required Domains

{domains}

## Required DNS Records

{records}

## Required Domain/DNS Controls

{controls}

## Required Production Validation

{validation}

## Domain/DNS Safety Rules

- Keep backend and frontend production URLs explicit.
- Do not expose backend-only secret routes publicly unless protected.
- Keep CORS restricted to the production frontend domain.
- Use HTTPS only for production access.
- Confirm frontend-to-backend calls work from the production domain.
- Confirm email DNS records before sending production emails at volume.

## Release Decision

- Can continue: `True`
- Next step: CORS/security production configuration pack.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_119_DOMAIN_DNS_PRODUCTION_CONFIG_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("secret_values_included", pack["secret_values_included"])
print("can_continue", pack["release_decision"]["can_continue"])
print("STEP_119_OK")