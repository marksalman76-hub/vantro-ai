from pathlib import Path

terms = [
    "JWT_SECRET",
    "jwt.encode",
    "jwt.decode",
    "create_access_token",
    "generate_token",
    "owner_admin",
    "admin_token",
    "access_token",
]

for file in Path("backend").rglob("*.py"):
    text = file.read_text(encoding="utf-8", errors="ignore")
    if any(term in text for term in terms):
        print("\n" + "=" * 90)
        print(file)
        print("=" * 90)
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if any(term in line for term in terms):
                start = max(0, i - 8)
                end = min(len(lines), i + 14)
                print(f"\n--- around line {i + 1} ---")
                for n in range(start, end):
                    print(f"{n + 1}: {lines[n]}")