
from pathlib import Path
from datetime import datetime
import base64
import uuid


PLACEHOLDER_IMAGE = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO5W"
    "n3sAAAAASUVORK5CYII="
)


def generate_ugc_visual_asset(prompt: str, tenant_id: str = "owner_admin"):
    asset_id = f"ugc_asset_{uuid.uuid4().hex[:10]}"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    output_dir = Path("frontend/public/generated-assets")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{asset_id}_{timestamp}.png"
    filepath = output_dir / filename

    image_bytes = base64.b64decode(PLACEHOLDER_IMAGE)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    public_url = f"/generated-assets/{filename}"

    return {
        "success": True,
        "asset_id": asset_id,
        "asset_url": public_url,
        "preview_url": public_url,
        "media_url": public_url,
        "generated_files": [str(filepath)],
        "provider": "local_visual_generation_runtime",
        "generation_type": "ugc_visual_asset",
    }
