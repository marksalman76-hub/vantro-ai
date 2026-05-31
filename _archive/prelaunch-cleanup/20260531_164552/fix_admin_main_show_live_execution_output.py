from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/page.tsx")
backup = Path("backups") / f"admin_main_show_live_output_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

# Add output into fallback result message if result cards use item.message only.
s = s.replace(
'''          message:
            data?.message ||
            data?.summary ||
            data?.error ||
            "Live provider execution response received.",''',
'''          message:
            safeOutput?.text ||
            data?.output?.generated_output ||
            data?.output?.output ||
            data?.output?.content ||
            data?.message ||
            data?.summary ||
            data?.error ||
            "Live provider execution response received.",'''
)

# Replace generic card copy if present.
s = s.replace(
'''The agent returned a live provider result and is ready for review.''',
'''{item.message || "The live provider output is ready for review."}'''
)

s = s.replace(
'''The agent returned a governed result and is ready for review.''',
'''{item.message || "The live provider output is ready for review."}'''
)

p.write_text(s, encoding="utf-8")

print("ADMIN_MAIN_LIVE_OUTPUT_RENDERING_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {p}")