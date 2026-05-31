from pathlib import Path
import re

root = Path.cwd()

targets = [
    "frontend/src/app/client/page.tsx",
    "frontend/src/app/login/page.tsx",
    "frontend/src/app/signup/page.tsx",
    "frontend/src/app/admin/page.tsx",
    "frontend/src/app/admin-login/page.tsx",
    "frontend/src/app/client/billing/page.tsx",
]

fixed = []

for rel in targets:
    path = root / rel

    if not path.exists():
        continue

    text = path.read_text(encoding="utf-8")

    pattern = (
        r'export const dynamic = "force-dynamic";\s*'
        r'export const revalidate = 0;\s*'
        r'"use client";'
    )

    replacement = (
        '"use client";\n\n'
        'export const dynamic = "force-dynamic";\n'
        'export const revalidate = 0;'
    )

    updated = re.sub(pattern, replacement, text, flags=re.MULTILINE)

    if updated != text:
        path.write_text(updated, encoding="utf-8")
        fixed.append(rel)

print("USE_CLIENT_DYNAMIC_ORDER_FIXED")
for item in fixed:
    print("-", item)