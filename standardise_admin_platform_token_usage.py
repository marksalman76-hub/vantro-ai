from pathlib import Path
from datetime import datetime

FILES = [
    Path("live_all_agent_execution_sweep.py"),
    Path("live_canonical_agent_execution_sweep.py"),
    Path("live_verify_admin_proxy_run_agent_auth.py"),
    Path("live_verify_admin_proxy_agents_unique.py"),
    Path("live_verify_admin_agent_execution_certification.py"),
]

backup_dir = Path("backups") / ("admin_platform_token_standardise_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

changed = []

for path in FILES:
    if not path.exists():
        continue

    text = path.read_text(encoding="utf-8")
    backup = backup_dir / path.name
    backup.write_text(text, encoding="utf-8")

    original = text

    text = text.replace('os.getenv("ADMIN_TOKEN"', 'os.getenv("ADMIN_PLATFORM_TOKEN"')
    text = text.replace("os.getenv('ADMIN_TOKEN'", "os.getenv('ADMIN_PLATFORM_TOKEN'")
    text = text.replace('"ADMIN_TOKEN"', '"ADMIN_PLATFORM_TOKEN"')
    text = text.replace("'ADMIN_TOKEN'", "'ADMIN_PLATFORM_TOKEN'")
    text = text.replace("Set ADMIN_TOKEN first.", "Set ADMIN_PLATFORM_TOKEN first.")
    text = text.replace("ADMIN_TOKEN_SET", "ADMIN_PLATFORM_TOKEN_SET")

    if text != original:
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

print("ADMIN_PLATFORM_TOKEN_STANDARDISED")
print("Backup:", backup_dir)
print("Changed files:")
for item in changed:
    print("-", item)