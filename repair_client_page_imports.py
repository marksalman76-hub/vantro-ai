from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")

text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"client_page_before_import_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Remove ALL existing React imports
text = re.sub(
    r'import\s+React.*?from\s+"react";\s*',
    '',
    text
)

text = re.sub(
    r'import\s+\{\s*useEffect,\s*useState\s*\}\s+from\s+"react";\s*',
    '',
    text
)

# Remove duplicate use client directives
text = re.sub(
    r'"use client";\s*',
    '',
    text
)

# Rebuild proper file header
fixed_header = '''"use client";

import React, { useEffect, useRef, useState } from "react";

'''

text = fixed_header + text.lstrip()

path.write_text(text, encoding="utf-8")

print("CLIENT_PAGE_IMPORTS_REPAIRED")
print(f"Backup: {backup}")