from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_profile_dropdown_click_outside_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

if 'useRef' not in text:
    text = text.replace(
        'import React, { useEffect, useState } from "react";',
        'import React, { useEffect, useRef, useState } from "react";',
        1,
    )

if "const profileMenuRef = useRef<HTMLDetailsElement | null>(null);" not in text:
    marker = '  const [darkModeEnabled, setDarkModeEnabled] = useState(false);'
    if marker not in text:
        raise SystemExit("Could not find state insertion marker.")
    text = text.replace(
        marker,
        marker + '\n  const profileMenuRef = useRef<HTMLDetailsElement | null>(null);',
        1,
    )

if "handleProfileMenuOutsideClick" not in text:
    insert_marker = "\n  async function loadBusinessProfile()"
    effect_block = '''
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
  }, []);

'''
    if insert_marker not in text:
        raise SystemExit("Could not find loadBusinessProfile function insertion point.")
    text = text.replace(insert_marker, effect_block + insert_marker, 1)

if '<details ref={profileMenuRef}' not in text:
    if '<details style={{ position: "relative", zIndex: 100 }}>' in text:
        text = text.replace(
            '<details style={{ position: "relative", zIndex: 100 }}>',
            '<details ref={profileMenuRef} style={{ position: "relative", zIndex: 100 }}>',
            1,
        )
    elif '<details style={{ position: "relative" }}>' in text:
        text = text.replace(
            '<details style={{ position: "relative" }}>',
            '<details ref={profileMenuRef} style={{ position: "relative", zIndex: 100 }}>',
            1,
        )
    else:
        raise SystemExit("Could not find profile details tag.")

path.write_text(text, encoding="utf-8")

print("PROFILE_DROPDOWN_CLICK_OUTSIDE_V2_FIXED")
print(f"Backup: {backup}")