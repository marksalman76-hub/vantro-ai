from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_profile_dropdown_click_outside_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
    'import React, { useEffect, useState } from "react";',
    'import React, { useEffect, useRef, useState } from "react";'
)

state_marker = '  const [darkModeEnabled, setDarkModeEnabled] = useState(false);'
replacement = '''  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const profileMenuRef = useRef<HTMLDetailsElement | null>(null);'''

if state_marker not in text:
    raise SystemExit("Could not find darkModeEnabled state marker.")

text = text.replace(state_marker, replacement, 1)

effect_marker = '  useEffect(() => {\n    loadBusinessProfile();\n  }, []);'
effect_replacement = '''  useEffect(() => {
    loadBusinessProfile();
  }, []);

  useEffect(() => {
    function handleProfileMenuOutsideClick(event: MouseEvent) {
      const menu = profileMenuRef.current;
      if (!menu) return;
      if (!menu.open) return;
      if (event.target instanceof Node && menu.contains(event.target)) return;
      menu.open = false;
    }

    document.addEventListener("mousedown", handleProfileMenuOutsideClick);
    return () => document.removeEventListener("mousedown", handleProfileMenuOutsideClick);
  }, []);'''

if effect_marker not in text:
    raise SystemExit("Could not find loadBusinessProfile useEffect marker.")

text = text.replace(effect_marker, effect_replacement, 1)

text = text.replace(
    '<details style={{ position: "relative", zIndex: 100 }}>',
    '<details ref={profileMenuRef} style={{ position: "relative", zIndex: 100 }}>',
    1
)

path.write_text(text, encoding="utf-8")

print("PROFILE_DROPDOWN_CLICK_OUTSIDE_FIXED")
print(f"Backup: {backup}")