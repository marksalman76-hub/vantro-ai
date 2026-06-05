from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

PRODUCT_LIBRARY = ROOT / "backend" / "app" / "runtime" / "creative_product_asset_library.py"
MEDIA_REGISTRY = ROOT / "backend" / "app" / "runtime" / "creative_asset_persistence_bridge.py"

backup_dir = ROOT / "backups" / f"durable_creative_asset_persistence_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

for path in [PRODUCT_LIBRARY, MEDIA_REGISTRY]:
    if path.exists():
        (backup_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

# Patch product/reference asset library.
text = PRODUCT_LIBRARY.read_text(encoding="utf-8")

text = text.replace(
'''ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "runtime_outputs" / "creative_product_assets"
REGISTRY_PATH = ASSET_ROOT / "creative_product_asset_registry.json"''',
'''ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ASSET_ROOT = ROOT / "runtime_outputs" / "creative_product_assets"
ASSET_ROOT = Path(os.getenv("CREATIVE_ASSET_PERSISTENCE_DIR", str(DEFAULT_ASSET_ROOT)))
REGISTRY_PATH = ASSET_ROOT / "creative_product_asset_registry.json"'''
)

if '"persistence_mode":' not in text:
    text = text.replace(
'''        "verified_at": _now(),
    }''',
'''        "persistence_mode": "durable" if os.getenv("CREATIVE_ASSET_PERSISTENCE_DIR") else "local_runtime_fallback",
        "persistence_root": str(ASSET_ROOT),
        "verified_at": _now(),
    }'''
    )

    text = text.replace(
'''        "verified_at": _now(),
    }''',
'''        "persistence_mode": "durable" if os.getenv("CREATIVE_ASSET_PERSISTENCE_DIR") else "local_runtime_fallback",
        "persistence_root": str(ASSET_ROOT),
        "verified_at": _now(),
    }'''
    )

PRODUCT_LIBRARY.write_text(text, encoding="utf-8")

# Patch generated media persistence bridge.
if MEDIA_REGISTRY.exists():
    media = MEDIA_REGISTRY.read_text(encoding="utf-8")

    replacements = [
        (
'''ROOT = Path(__file__).resolve().parents[3]
REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"''',
'''ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"
REGISTRY_DIR = Path(os.getenv("CREATIVE_MEDIA_PERSISTENCE_DIR", str(DEFAULT_REGISTRY_DIR)))'''
        ),
        (
'''ROOT = Path(__file__).resolve().parents[3]
ASSET_REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"''',
'''ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ASSET_REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"
ASSET_REGISTRY_DIR = Path(os.getenv("CREATIVE_MEDIA_PERSISTENCE_DIR", str(DEFAULT_ASSET_REGISTRY_DIR)))'''
        ),
        (
'''CREATIVE_ASSET_REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"''',
'''DEFAULT_CREATIVE_ASSET_REGISTRY_DIR = ROOT / "runtime_outputs" / "creative_asset_registry"
CREATIVE_ASSET_REGISTRY_DIR = Path(os.getenv("CREATIVE_MEDIA_PERSISTENCE_DIR", str(DEFAULT_CREATIVE_ASSET_REGISTRY_DIR)))'''
        ),
    ]

    for old, new in replacements:
        if old in media:
            media = media.replace(old, new)

    if "import os" not in media[:500]:
        media = media.replace("import json", "import json\nimport os", 1)

    if "persistence_mode" not in media:
        media = media.replace(
'''"credential_values_exposed": False''',
'''"credential_values_exposed": False,
        "persistence_mode": "durable" if os.getenv("CREATIVE_MEDIA_PERSISTENCE_DIR") else "local_runtime_fallback",
        "persistence_root": str(REGISTRY_DIR) if "REGISTRY_DIR" in globals() else str(globals().get("ASSET_REGISTRY_DIR", globals().get("CREATIVE_ASSET_REGISTRY_DIR", "")))''',
        1,
        )

    MEDIA_REGISTRY.write_text(media, encoding="utf-8")

print("DURABLE_CREATIVE_ASSET_PERSISTENCE_INSTALLED")
print("Updated:", PRODUCT_LIBRARY)
print("Updated:", MEDIA_REGISTRY)
print("Backup:", backup_dir)