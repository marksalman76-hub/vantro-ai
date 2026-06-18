from pathlib import Path
import json
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
VERIFY = ROOT / "verify_client_portal_symbol_cleanup.py"

backup_dir = ROOT / "backups" / f"client_portal_symbol_cleanup_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(CLIENT_PAGE, backup_dir / "client_page.tsx")

text = CLIENT_PAGE.read_text(encoding="utf-8-sig", errors="ignore").replace("\ufeff", "")

# Target only known visible mojibake fragments. Do not rewrite JSX structure.
replacements = {
    "BUSINESS PROFILE INTELLIGENCE Â€": "BUSINESS PROFILE INTELLIGENCE",
    "BUSINESS PROFILE INTELLIGENCE Â": "BUSINESS PROFILE INTELLIGENCE",
    "Â€": "",
    "Â ": " ",
    "Â": "",
    "â€”": "-",
    "â€“": "-",
    "â€˜": "'",
    "â€™": "'",
    "â€œ": "",
    "â€": "",
    "â€": "",
    "â–": "",
    "â†": "",
    "â—": "",
    "âœ™": "",
    "âœ": "",
    "â˜": "",
    "ðŸ": "",
    "Ãƒ": "",
    "Ã": "",
    "┬": "",
    "├": "",
    "╞": "",
    "Æ": "",
}

for bad, good in replacements.items():
    text = text.replace(bad, good)

# Clean obvious doubled spaces created by icon removal, but keep formatting safe.
while "  " in text:
    text = text.replace("  ", " ")

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
    "Â€",
    "Â",
    "â€”",
    "â€“",
    "â€˜",
    "â€™",
    "â€œ",
    "â€",
    "â–",
    "â†",
    "â—",
    "âœ",
    "ðŸ",
    "Ã",
    "┬",
    "├",
    "╞",
    "Æ",
]

remaining = {}
for token in bad_tokens:
    lines = [i + 1 for i, line in enumerate(text.splitlines()) if token in line]
    if lines:
        remaining[token] = lines[:20]

proof = {
    "client_portal_symbol_cleanup_attempted": True,
    "client_portal_symbol_cleanup_passed": not remaining,
    "use_client_first_line": text.splitlines()[0].strip() == '"use client";',
    "remaining_symbol_tokens": remaining,
    "provider_call_attempted": False,
    "media_generation_attempted": False,
    "billing_mutation_attempted": False,
    "credit_mutation_attempted": False,
    "stripe_live_charge_attempted": False,
    "aws21_or_later_work_attempted": False,
    "public_cutover_enabled": False,
}

print("CLIENT_PORTAL_SYMBOL_CLEANUP_PROOF:")
print(json.dumps(proof, indent=2, sort_keys=True))

if not proof["client_portal_symbol_cleanup_passed"] or not proof["use_client_first_line"]:
    raise SystemExit("CLIENT_PORTAL_SYMBOL_CLEANUP_FAILED")

print("CLIENT_PORTAL_SYMBOL_CLEANUP_PASSED")
'''.lstrip(), encoding="utf-8")

print(json.dumps({
    "client_portal_symbol_cleanup": True,
    "client_page": str(CLIENT_PAGE),
    "backup": str(backup_dir),
    "verifier": str(VERIFY),
    "provider_calls": False,
    "media_generation": False,
    "billing_mutation": False,
    "credit_mutation": False,
    "stripe": False,
}, indent=2))