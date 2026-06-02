from pathlib import Path

p = Path("backend/app/main.py")
text = p.read_text(encoding="utf-8")

text = text.replace(
    '''        or package_tier_clean in {"owner_managed", "manual_deployment", "demo", "internal"}''',
    ""
)

text = text.replace(
    '''    package_tier_clean = str(getattr(request, "package_tier", "") or "").strip().lower()
''',
    ""
)

p.write_text(text, encoding="utf-8")

print("PACKAGE_TIER_RUNTIME_REFERENCE_REMOVED")