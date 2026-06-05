from pathlib import Path

ROOT = Path.cwd()
home = ROOT / "frontend/src/app/page.tsx"

text = home.read_text(encoding="utf-8")
original = text

text = text.replace('import HomepageSupportClient from "./homepage-support-client";\n', "")
text = text.replace("      <HomepageSupportClient />\n", "")

home.write_text(text, encoding="utf-8")

if text != original:
    print("REMOVED_DUPLICATE_HOMEPAGE_SUPPORT_WIDGET")
else:
    print("NO_DUPLICATE_HOMEPAGE_SUPPORT_WIDGET_CHANGE")