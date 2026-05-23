from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_useref_import_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = re.sub(
    r'import React,\s*\{\s*([^}]+?)\s*\}\s*from "react";',
    lambda m: 'import React, { ' + ", ".join(
        sorted(set([x.strip() for x in m.group(1).split(",")] + ["useRef"]))
    ) + ' } from "react";',
    text,
    count=1,
)

if "useRef" not in text.split("\n", 5)[0:5].__str__():
    raise SystemExit("useRef import was not installed safely.")

path.write_text(text, encoding="utf-8")

print("USEREF_IMPORT_FIXED")
print(f"Backup: {backup}")