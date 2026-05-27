from pathlib import Path
import hashlib

ROOT = Path.cwd()

targets = [
    ROOT / "frontend/src/app/admin/page.tsx",
]

for target in targets:
    print("=" * 80)
    print("FILE:", target)
    print("EXISTS:", target.exists())

    if target.exists():
        text = target.read_text(encoding="utf-8", errors="ignore")

        print("SHA256:", hashlib.sha256(text.encode("utf-8")).hexdigest())
        print()

        markers = [
            "Admin Command Centre",
            "Owner Control Plane",
            "Readiness Panel",
            "Owner Governance Rules",
        ]

        for marker in markers:
            print(marker, "=>", marker in text)

        print()
        print(text[:4000])