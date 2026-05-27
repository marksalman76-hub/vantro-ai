from pathlib import Path
import hashlib

keys = ["ADMIN_PLATFORM_TOKEN", "ADMIN_AUTH_SECRET"]
files = [".env.local", ".env"]

for file_name in files:
    path = Path(file_name)
    print("FILE", file_name, "exists=", path.exists())

    if not path.exists():
        continue

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()

        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)

        if key.strip() in keys:
            value = value.strip().strip('"').strip("'")
            print(
                key.strip(),
                "present length=",
                len(value),
                "sha_prefix=",
                hashlib.sha256(value.encode()).hexdigest()[:10],
            )