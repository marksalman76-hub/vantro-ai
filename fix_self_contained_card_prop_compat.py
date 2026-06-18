from pathlib import Path
import json
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent
COMPONENT = ROOT / "frontend" / "src" / "components" / "ClientCreateMediaProductionCard.tsx"

backup_dir = ROOT / "backups" / f"self_contained_card_prop_compat_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(COMPONENT, backup_dir / "ClientCreateMediaProductionCard.tsx")

text = COMPONENT.read_text(encoding="utf-8-sig", errors="ignore").replace("\ufeff", "")

if "type ClientCreateMediaProductionCardProps" not in text:
    text = text.replace(
        'import { useState } from "react";',
        'import { useState } from "react";\n\n'
        'type ClientCreateMediaProductionCardProps = {\n'
        '  onOpenCreateMedia?: () => void;\n'
        '};',
        1,
    )

text = text.replace(
    "export default function ClientCreateMediaProductionCard() {",
    "export default function ClientCreateMediaProductionCard({\n"
    "  onOpenCreateMedia,\n"
    "}: ClientCreateMediaProductionCardProps) {",
    1,
)

text = text.replace(
    'onClick={() => setRequestOpen((value) => !value)}',
    'onClick={() => {\n'
    '            onOpenCreateMedia?.();\n'
    '            setRequestOpen((value) => !value);\n'
    '          }}',
    1,
)

body = "\n".join(line.rstrip() for line in text.splitlines()).strip()
text = body + "\n"

COMPONENT.write_text(text, encoding="utf-8", newline="\n")

print(json.dumps({
    "prop_compat_fixed": True,
    "component": str(COMPONENT),
    "backup": str(backup_dir),
    "provider_calls": False,
    "media_generation": False,
    "billing_mutation": False,
    "credit_mutation": False,
    "stripe": False,
}, indent=2))