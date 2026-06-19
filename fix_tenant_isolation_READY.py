#!/usr/bin/env python3
"""
VANTRO.AI SECURITY FIX #1: Tenant Isolation
Removes all default tenant_id values - makes tenant_id REQUIRED
"""
import re
from pathlib import Path

def fix_tenant_isolation():
    main_py = Path("backend/app/main.py")

    if not main_py.exists():
        print(f"❌ ERROR: {main_py} not found")
        print("Make sure you're in repo root: C:\\Users\\User\\Desktop\\ecommerce-ai-agent-platform")
        return False

    print("🔧 Fixing tenant isolation vulnerabilities...")
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()

    original_count = content.count('default="client_demo_001"')

    # FIX: Remove all tenant_id defaults
    content = re.sub(
        r'x_tenant_id:\s*str\s*=\s*Header\(\s*default\s*=\s*"[^"]*"\s*\)',
        'x_tenant_id: str = Header(...)',
        content
    )

    # FIX: Remove other demo tenant defaults
    content = re.sub(
        r'default\s*=\s*"(?:client_demo_001|owner_managed_demo|manual_deployment_client)"',
        '',
        content
    )

    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ FIXED: Removed {original_count} instances of tenant_id defaults")
    print("✅ ENFORCED: tenant_id now REQUIRED on all endpoints")
    print("✅ BEHAVIOR: Missing tenant_id → 401 Unauthorized (fail hard)")
    print("\n📋 Next steps:")
    print("  1. git diff backend/app/main.py")
    print("  2. git add backend/app/main.py")
    print("  3. git commit -m 'Security: Remove tenant isolation fallback vulnerability'")
    print("  4. git push")
    return True

if __name__ == "__main__":
    fix_tenant_isolation()
