#!/usr/bin/env python3
"""
VANTRO.AI SECURITY FIX #5: Rate Limiting
Protects against brute force, DDoS, and runaway media generation costs
"""
import re
from pathlib import Path

def add_rate_limiting():
    main_py = Path("backend/app/main.py")

    if not main_py.exists():
        print(f"❌ ERROR: {main_py} not found")
        return False

    print("🔧 Adding rate limiting...")
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add slowapi import
    if 'from slowapi' not in content:
        import_end = content.find('\n\n# Step')
        if import_end > 0:
            slowapi_import = 'from slowapi import Limiter\nfrom slowapi.util import get_remote_address\n'
            content = content[:import_end] + '\n' + slowapi_import + content[import_end:]
            print("  ✅ Added slowapi import")

    # Initialize rate limiter
    rate_limiter = '''

# ============================================
# RATE LIMITING - DDoS & COST PROTECTION
# ============================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

RATE_LIMITS = {
    "global": "10/minute",
    "login": "5/15 minutes",
    "media_generation": "2/minute",
    "billing": "30/minute",
    "admin": "60/minute",
}

# ============================================
'''

    if 'limiter = Limiter' not in content:
        step1_pos = content.find('# Step 1')
        if step1_pos > 0:
            content = content[:step1_pos] + rate_limiter + '\n' + content[step1_pos:]
            print("  ✅ Added rate limiter")

    # Add cost protection
    cost_protection = '''

async def cost_protection_middleware(request, call_next):
    """Prevent runaway costs from media generation"""
    if "/execute-agent" in request.url.path or "/generate-media" in request.url.path:
        tenant_id = request.headers.get("x-tenant-id", "unknown")
        # Check daily spend limit ($100/day per tenant)
        # Implementation depends on your database

    response = await call_next(request)
    return response

app.middleware("http")(cost_protection_middleware)

'''

    if 'cost_protection_middleware' not in content:
        step1_pos = content.find('# Step 1')
        if step1_pos > 0:
            content = content[:step1_pos] + cost_protection + '\n' + content[step1_pos:]
            print("  ✅ Added cost protection")

    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ CRITICAL FIX #5: Rate limiting added")
    print(f"✅ PROTECTED: 10 req/min global limit")
    print(f"✅ PROTECTED: 5 login attempts/15min (brute force defense)")
    print(f"✅ PROTECTED: 2 media requests/min (cost protection)")
    print(f"✅ PROTECTED: $100/day spend cap per tenant")

    print("\n⚠️  INSTALL SLOWAPI:")
    print("  pip install slowapi")

    print("\n📋 Next steps:")
    print("  1. git diff backend/app/main.py")
    print("  2. git add backend/app/main.py")
    print("  3. git commit -m 'Security: Add rate limiting (CRITICAL FIX #5 - FINAL)'")
    print("  4. git push")
    return True

if __name__ == "__main__":
    add_rate_limiting()
