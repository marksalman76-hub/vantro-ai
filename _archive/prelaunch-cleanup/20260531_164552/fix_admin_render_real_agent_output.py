from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/page.tsx")

backup = Path("backups") / f"admin_real_output_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

old = '''                          const cleanMessage = item?.success
                            ? "Agent pipeline completed successfully."
                            : item?.message === "Execution response received."
                            ? "The agent returned a live provider result and is ready for operator review."
                            : item?.message || "Review the governed result before delivery.";'''

new = '''                          const liveOutput =
                            item?.output ||
                            item?.generated_output ||
                            item?.response ||
                            item?.provider_output ||
                            item?.message;

                          const cleanMessage = item?.success
                            ? liveOutput || "Agent pipeline completed successfully."
                            : item?.message === "Execution response received."
                            ? "The agent returned a live provider result and is ready for operator review."
                            : item?.message || "Review the governed result before delivery.";'''

s = s.replace(old, new)

p.write_text(s, encoding="utf-8")

print("ADMIN_REAL_OUTPUT_RENDER_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {p}")