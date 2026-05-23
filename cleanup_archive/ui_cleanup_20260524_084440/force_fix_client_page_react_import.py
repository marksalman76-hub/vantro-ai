from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_force_react_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

lines = text.splitlines()
fixed = False

for i, line in enumerate(lines):
    if line.startswith("import React"):
        lines[i] = 'import React, { useEffect, useRef, useState } from "react";'
        fixed = True
        break

if not fixed:
    lines.insert(0, 'import React, { useEffect, useRef, useState } from "react";')

text = "\n".join(lines) + "\n"

if 'import React, { useEffect, useRef, useState } from "react";' not in text:
    raise SystemExit("React import still not fixed.")

path.write_text(text, encoding="utf-8")

print("CLIENT_PAGE_REACT_IMPORT_FORCE_FIXED")
print(f"Backup: {backup}")