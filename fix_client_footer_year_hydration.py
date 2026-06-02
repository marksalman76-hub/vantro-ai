from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''┬⌐ {new Date().getFullYear()} E-commerce AI Agent Platform'''
new = '''© 2026 E-commerce AI Agent Platform'''

if old not in text:
    raise SystemExit("footer year hydration anchor not found")

text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")
print("CLIENT_FOOTER_YEAR_HYDRATION_FIXED")