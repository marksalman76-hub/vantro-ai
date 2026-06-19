#!/usr/bin/env python3
"""
VANTRO.AI SECURITY FIX #2: Remove Hardcoded Demo IDs
Removes 22 hardcoded demo tenant references
"""
import re
from pathlib import Path

def fix_hardcoded_demo_ids():
    main_py = Path("backend/app/main.py")

    if not main_py.exists():
        print(f"❌ ERROR: {main_py} not found")
        return False

    print("🔧 Removing hardcoded demo IDs...")
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()

    original_count = content.count('client_demo_001') + content.count('owner_managed_demo')

    # REPLACE: client_demo_001 with env var
    content = re.sub(
        r'"client_demo_001"',
        'os.getenv("DEMO_TENANT_ID", "demo_001")',
        content
    )

    # REPLACE: owner_managed_demo with env var
    content = re.sub(
        r'"owner_managed_demo"',
        'os.getenv("OWNER_TENANT_ID", "owner_001")',
        content
    )

    # REPLACE: owner_managed_demo_client
    content = re.sub(
        r'"owner_managed_demo_client"',
        'os.getenv("OWNER_MANAGED_TENANT_ID", "owner_managed_001")',
        content
    )

    # REPLACE: manual_deployment_client
    content = re.sub(
        r'"manual_deployment_client"',
        'os.getenv("MANUAL_TENANT_ID", "manual_001")',
        content
    )

    # Ensure os is imported
    if 'import os' not in content:
        insert_pos = content.find('import')
        if insert_pos != -1:
            content = content[:insert_pos] + 'import os\n' + content[insert_pos:]

    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ FIXED: Removed {original_count} hardcoded demo IDs")
    print("✅ Replaced with environment variables")
    print("\n📋 Next steps:")
    print("  1. git diff backend/app/main.py")
    print("  2. git add backend/app/main.py")
    print("  3. git commit -m 'Security: Remove hardcoded demo IDs (CRITICAL FIX #2)'")
    print("  4. git push")
    return True

if __name__ == "__main__":
    fix_hardcoded_demo_ids()
