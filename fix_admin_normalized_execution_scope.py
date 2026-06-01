from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"

BACKUP = ROOT / "backups" / f"admin_normalized_execution_scope_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "page.tsx")

s = TARGET.read_text(encoding="utf-8")

# Add component-level normalized packet after result state if missing.
if "const normalizedResult = normalizeExecutionPacket(result);" not in s:
    s = s.replace(
        'const [result, setResult] = useState<any>(null);',
        'const [result, setResult] = useState<any>(null);\n  const normalizedResult = normalizeExecutionPacket(result);'
    )

# JSX should use normalizedResult, not local handler variable normalizedExecution.
s = s.replace("normalizedExecution?.performed", "normalizedResult?.performed")
s = s.replace("normalizedExecution.performed", "normalizedResult.performed")
s = s.replace("normalizedExecution?.previewUrl", "normalizedResult?.previewUrl")
s = s.replace("normalizedExecution.previewUrl", "normalizedResult.previewUrl")

TARGET.write_text(s, encoding="utf-8")

print("ADMIN_NORMALIZED_EXECUTION_SCOPE_FIXED")
print("Backup:", BACKUP)