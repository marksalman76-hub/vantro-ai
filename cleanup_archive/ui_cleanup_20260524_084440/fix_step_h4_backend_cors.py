from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

path = ROOT / "backend" / "app" / "main.py"
text = path.read_text(encoding="utf-8", errors="ignore")

backup = BACKUPS / f"main_before_step_h4_backend_cors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(text, encoding="utf-8")

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

if "CORSMiddleware" in text and "ecommerce-ai-agent-platform.vercel.app" not in text:
    marker = "app = FastAPI"
    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError("Could not find FastAPI app declaration.")
    next_line = text.find("\n", idx)
    text = text[: next_line + 1] + "\n" + cors_block + "\n" + text[next_line + 1 :]

path.write_text(text, encoding="utf-8")

print("STEP_H4_BACKEND_CORS_INSTALLED")
print(f"Backup: {backup}")