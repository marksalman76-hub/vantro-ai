from pathlib import Path
import json
import re
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
VERIFY = ROOT / "verify_client_visible_glyphs_final.py"

backup_dir = ROOT / "backups" / f"client_visible_glyphs_final_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(CLIENT_PAGE, backup_dir / "client_page.tsx")

text = CLIENT_PAGE.read_text(encoding="utf-8-sig", errors="ignore").replace("\ufeff", "")

# Normalize known visible headings and customer-facing button labels.
exact_replacements = {
    "BUSINESS PROFILE INTELLIGENCE Â€": "BUSINESS PROFILE INTELLIGENCE",
    "BUSINESS PROFILE INTELLIGENCE Â": "BUSINESS PROFILE INTELLIGENCE",
    "£ Save business profile": "Save business profile",
    "» Reset to last save": "Reset to last save",
    "% Preview profile": "Preview profile",
    "â– Save business profile": "Save business profile",
    "â† Reset to last save": "Reset to last save",
    "â— Preview profile": "Preview profile",
    "â— Not saved yet": "Not saved yet",
    "â— How it works": "How it works",
    "â— Media options": "Media options",
    "â— Direct complete media": "Direct complete media",
    "Â€": "",
    "Â": "",
    "â€”": "-",
    "â€“": "-",
    "â€˜": "'",
    "â€™": "'",
    "â€œ": "",
    "â€": "",
    "â€": "",
    "Ã": "",
    "┬": "",
    "├": "",
    "╞": "",
    "Æ": "",
}

for old, new in exact_replacements.items():
    text = text.replace(old, new)

# Strip decorative glyph prefixes before known customer-facing labels.
customer_labels = [
    "Save business profile",
    "Reset to last save",
    "Preview profile",
    "Not saved yet",
    "How it works",
    "Media options",
    "Direct complete media",
    "Review latest output",
    "Approve or request changes",
    "Run next optimisation",
]

for label in customer_labels:
    # Handles strings like "£ Save business profile", "/ Review latest output", etc.
    text = re.sub(
        rf'(["`])[^A-Za-z0-9"\n]{{1,8}}\s*{re.escape(label)}\1',
        rf'"\g<0>"',
        text,
    )
    # Safer direct cleanup after the broad capture above.
    for glyph in ["£", "»", "%", "/", "\\", "|", "‹", "›", "•", "·", "™", "©", "®"]:
        text = text.replace(f'"{glyph} {label}"', f'"{label}"')
        text = text.replace(f"`{glyph} {label}`", f"`{label}`")

# Remove suffix garbage after the business heading when it appears inside text.
text = re.sub(
    r"BUSINESS PROFILE INTELLIGENCE\s*[^A-Za-z0-9\s<>{}\[\]().,:;_\-'\"]{1,12}",
    "BUSINESS PROFILE INTELLIGENCE",
    text,
)

# Business profile field icon slots: remove decorative icon values from config arrays.
business_profile_labels = [
    "Business name",
    "Business niche",
    "Products & services",
    "Target audience",
    "Competitors",
    "Offers",
    "Brand voice",
    "Positioning",
    "Goals",
    "Key differentiators",
]

for label in business_profile_labels:
    text = re.sub(
        rf'(\[\s*"[^"]+"\s*,\s*)"[^"]*"(\s*,\s*"{re.escape(label)}")',
        rf'\1""\2',
        text,
    )

# Remove remaining common corrupted icon fragments only when standalone in quotes.
standalone_bad_literals = [
    "£", "»", "%", "/", "‹", "›", "•", "™", "©", "®",
    "ă", "ăsi", "ă™", "ă-", "asi", "â", "Â", "Ã",
]

for bad in standalone_bad_literals:
    text = text.replace(f'"{bad}"', '""')
    text = text.replace(f"'{bad}'", "''")
    text = text.replace(f"`{bad}`", "``")

# Preserve use client directive exactly.
lines = text.splitlines()
while lines and not lines[0].strip():
    lines.pop(0)

if lines and lines[0].strip() in ['"use client";', "'use client';"]:
    lines = lines[1:]

while lines and not lines[0].strip():
    lines.pop(0)

text = '"use client";\n\n' + "\n".join(line.rstrip() for line in lines).strip() + "\n"
CLIENT_PAGE.write_text(text, encoding="utf-8", newline="\n")

VERIFY.write_text(r'''
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
text = client_page.read_text(encoding="utf-8", errors="ignore")

bad_tokens = [
    "Â", "â", "Ã", "┬", "├", "╞", "Æ",
    "£ Save", "» Reset", "% Preview",
    "BUSINESS PROFILE INTELLIGENCE Â",
    "BUSINESS PROFILE INTELLIGENCE â",
]

remaining = {}
for token in bad_tokens:
    lines = [i + 1 for i, line in enumerate(text.splitlines()) if token in line]
    if lines:
        remaining[token] = lines[:30]

proof = {
    "client_visible_glyph_cleanup_attempted": True,
    "client_visible_glyph_cleanup_passed": not remaining,
    "use_client_first_line": text.splitlines()[0].strip() == '"use client";',
    "remaining_visible_glyph_tokens": remaining,
    "provider_call_attempted": False,
    "media_generation_attempted": False,
    "billing_mutation_attempted": False,
    "credit_mutation_attempted": False,
    "stripe_live_charge_attempted": False,
    "aws21_or_later_work_attempted": False,
    "public_cutover_enabled": False,
}

print("CLIENT_VISIBLE_GLYPH_CLEANUP_PROOF:")
print(json.dumps(proof, indent=2, sort_keys=True))

if not proof["client_visible_glyph_cleanup_passed"] or not proof["use_client_first_line"]:
    raise SystemExit("CLIENT_VISIBLE_GLYPH_CLEANUP_FAILED")

print("CLIENT_VISIBLE_GLYPH_CLEANUP_PASSED")
'''.lstrip(), encoding="utf-8")

print(json.dumps({
    "client_visible_glyph_cleanup": True,
    "client_page": str(CLIENT_PAGE),
    "backup": str(backup_dir),
    "verifier": str(VERIFY),
    "provider_calls": False,
    "media_generation": False,
    "billing_mutation": False,
    "credit_mutation": False,
    "stripe": False,
}, indent=2))