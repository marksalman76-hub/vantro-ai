from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

main_path = ROOT / "backend" / "app" / "main.py"
bad_backup = BACKUPS / f"main_before_step_h4b_recover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
bad_backup.write_text(main_path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")

source_backup = ROOT / "backups" / "main_before_step_h4_backend_cors_20260519_181436.py"
if not source_backup.exists():
    raise RuntimeError("Expected backup not found: backups/main_before_step_h4_backend_cors_20260519_181436.py")

text = source_backup.read_text(encoding="utf-8", errors="ignore")

if "from fastapi.middleware.cors import CORSMiddleware" not in text:
    text = "from fastapi.middleware.cors import CORSMiddleware\n" + text

cors_block = '''
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ecommerce-ai-agent-platform.vercel.app",
        "https://ecommerce-ai-agent-platform-git-main-marksalman76-5799s-projects.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''

marker = "app = FastAPI("
idx = text.find(marker)
if idx == -1:
    marker = "app = FastAPI"
    idx = text.find(marker)

if idx == -1:
    raise RuntimeError("Could not find FastAPI app declaration.")

# Find end of app declaration by bracket balance.
paren_start = text.find("(", idx)
if paren_start == -1:
    line_end = text.find("\n", idx)
    insert_at = line_end + 1
else:
    depth = 0
    insert_at = None
    for pos in range(paren_start, len(text)):
        char = text[pos]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                insert_at = text.find("\n", pos)
                insert_at = len(text) if insert_at == -1 else insert_at + 1
                break
    if insert_at is None:
        raise RuntimeError("Could not find end of FastAPI app declaration.")

if "ecommerce-ai-agent-platform.vercel.app" not in text:
    text = text[:insert_at] + "\n" + cors_block + "\n" + text[insert_at:]

main_path.write_text(text, encoding="utf-8")

print("STEP_H4B_RECOVERED_AND_CORS_INSTALLED")
print(f"Broken backup: {bad_backup}")