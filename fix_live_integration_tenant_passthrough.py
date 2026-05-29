from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()

TARGETS = [
    ROOT / "backend/app/runtime/real_external_integration_execution_bridge.py",
    ROOT / "backend/app/runtime/real_action_execution_bridge.py",
    ROOT / "backend/app/core/integration_live_adapter_registry.py",
]

timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
backup_dir = ROOT / "backups" / f"live_integration_tenant_passthrough_before_{timestamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

patched = []

PATCH_BLOCK = '''
    tenant_id = (
        action_packet.get("tenant_id")
        or execution_packet.get("tenant_id")
        or runtime_context.get("tenant_id")
        or payload.get("tenant_id")
        or "client_demo_001"
    )
'''

for file_path in TARGETS:

    if not file_path.exists():
        continue

    text = file_path.read_text(encoding="utf-8")

    backup_target = backup_dir / file_path.name
    backup_target.write_text(text, encoding="utf-8")

    original = text

    if 'or "client_demo_001"' in text and "runtime_context.get" in text:
        print(f"SKIPPED (already patched): {file_path}")
        continue

    replacements = [
        (
            'tenant_id = action_packet.get("tenant_id", "client_demo_001")',
            PATCH_BLOCK.strip()
        ),
        (
            'tenant_id = execution_packet.get("tenant_id", "client_demo_001")',
            PATCH_BLOCK.strip()
        ),
        (
            'tenant_id = payload.get("tenant_id", "client_demo_001")',
            PATCH_BLOCK.strip()
        ),
        (
            'tenant_id = runtime_context.get("tenant_id", "client_demo_001")',
            PATCH_BLOCK.strip()
        ),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    passthrough_injection = """

    runtime_context = runtime_context or {}
    execution_packet = execution_packet or {}
    action_packet = action_packet or {}
    payload = payload or {}
"""

    if "runtime_context = runtime_context or {}" not in text:

        insertion_targets = [
            "def execute_real_external_action(",
            "def execute_integration_action(",
            "def route_live_provider_action(",
        ]

        for target in insertion_targets:
            idx = text.find(target)
            if idx != -1:
                body_start = text.find("):", idx)
                if body_start != -1:
                    body_start += 2
                    text = (
                        text[:body_start]
                        + passthrough_injection
                        + text[body_start:]
                    )
                    break

    if text != original:
        file_path.write_text(text, encoding="utf-8")
        patched.append(str(file_path))

print()
print("LIVE_INTEGRATION_TENANT_PASSTHROUGH_FIXED")
print(f"Backup folder: {backup_dir}")

for item in patched:
    print(f"Updated: {item}")