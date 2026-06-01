from pathlib import Path

p = Path("backend/app/runtime/ugc_visual_generation_runtime.py")

p.write_text(r'''
from datetime import datetime
import base64
import html
import uuid


def generate_ugc_visual_asset(prompt: str, tenant_id: str = "owner_admin"):
    asset_id = f"ugc_asset_{uuid.uuid4().hex[:10]}"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    safe_prompt = html.escape(str(prompt or "Premium UGC visual concept")[:260])

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#08111f"/>
      <stop offset="55%" stop-color="#13233f"/>
      <stop offset="100%" stop-color="#4c1d95"/>
    </linearGradient>
    <radialGradient id="glow" cx="70%" cy="30%" r="55%">
      <stop offset="0%" stop-color="#f9d5a7" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#f9d5a7" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="675" fill="url(#bg)"/>
  <rect width="1200" height="675" fill="url(#glow)"/>
  <circle cx="875" cy="255" r="150" fill="#f3d6bf" opacity="0.88"/>
  <circle cx="835" cy="230" r="18" fill="#2f1725"/>
  <circle cx="915" cy="230" r="18" fill="#2f1725"/>
  <path d="M820 310 Q875 355 930 310" stroke="#2f1725" stroke-width="12" fill="none" stroke-linecap="round"/>
  <rect x="760" y="430" width="230" height="140" rx="70" fill="#d6b39a" opacity="0.92"/>
  <rect x="145" y="120" width="390" height="455" rx="34" fill="#fff7ed" opacity="0.94"/>
  <rect x="220" y="185" width="240" height="250" rx="38" fill="#f5dcc8"/>
  <rect x="255" y="245" width="170" height="130" rx="26" fill="#ffffff" opacity="0.72"/>
  <text x="170" y="105" fill="#67e8f9" font-family="Arial" font-size="26" font-weight="800">GENERATED UGC VISUAL ASSET</text>
  <text x="170" y="625" fill="#f8fafc" font-family="Arial" font-size="30" font-weight="900">Luxury Skincare Creator Preview</text>
  <text x="560" y="140" fill="#ffffff" font-family="Arial" font-size="42" font-weight="900">Premium UGC Campaign</text>
  <text x="560" y="192" fill="#dbeafe" font-family="Arial" font-size="24">Visual concept generated from agent output</text>
  <foreignObject x="560" y="230" width="530" height="210">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Arial;color:#e2e8f0;font-size:22px;line-height:1.35;">
      {safe_prompt}
    </div>
  </foreignObject>
  <text x="560" y="520" fill="#fef3c7" font-family="Arial" font-size="24" font-weight="800">Preview asset ID: {asset_id}</text>
</svg>
""".strip()

    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    data_url = f"data:image/svg+xml;base64,{encoded}"

    return {
        "success": True,
        "asset_id": asset_id,
        "asset_url": data_url,
        "preview_url": data_url,
        "media_url": data_url,
        "generated_files": [],
        "provider": "local_visual_generation_runtime",
        "generation_type": "ugc_visual_asset",
        "created_at": timestamp,
    }
''', encoding="utf-8")

print("UGC_VISUAL_RUNTIME_NOW_RETURNS_DATA_URL")