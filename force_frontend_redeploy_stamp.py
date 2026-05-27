from pathlib import Path
from datetime import datetime, timezone

root = Path.cwd()
stamp = root / "frontend" / "src" / "app" / "deployment-stamp.ts"

value = datetime.now(timezone.utc).isoformat()

stamp.write_text(
    f'export const DEPLOYMENT_STAMP = "{value}";\n',
    encoding="utf-8",
)

print("FRONTEND_REDEPLOY_STAMP_UPDATED")
print(f"Updated: {stamp}")
print(f"Stamp: {value}")