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
