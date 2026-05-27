from pathlib import Path

root = Path("backend/app")
terms = [
    "invalid_token",
    "ADMIN_PLATFORM_TOKEN",
    "ADMIN_AUTH_SECRET",
    "Authorization",
    "bearer",
    "Bearer",
]

for file in root.rglob("*.py"):
    text = file.read_text(encoding="utf-8", errors="ignore")
    if any(term in text for term in terms):
        print(file)