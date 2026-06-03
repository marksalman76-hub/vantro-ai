from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"ugc_media_bridge_persist_assets_before_{STAMP}"

BRIDGE = ROOT / "backend" / "app" / "runtime" / "admin_ugc_live_media_execution_bridge.py"
FRONTEND_API = ROOT / "frontend" / "src" / "app" / "api" / "admin-creative-media-assets" / "route.ts"
TEST = ROOT / "test_ugc_media_bridge_persist_assets.py"

FRONTEND_API_CONTENT = r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
  "https://api.trance-formation.com.au";

const ADMIN_TOKEN =
  process.env.ADMIN_TOKEN ||
  process.env.ADMIN_PLATFORM_TOKEN ||
  process.env.OWNER_ADMIN_TOKEN ||
  "";

export async function GET() {
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (ADMIN_TOKEN) {
      headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
      headers["x-admin-token"] = ADMIN_TOKEN;
      headers["x-actor-role"] = "owner_admin";
    }

    const response = await fetch(`${BACKEND_BASE_URL}/admin/persisted-creative-assets`, {
      method: "GET",
      cache: "no-store",
      headers,
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        layer: "frontend_admin_creative_media_assets_proxy",
        status: "proxy_error",
        error: error instanceof Error ? error.message : String(error),
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
'''

TEST_CONTENT = r'''from pathlib import Path
import py_compile

bridge = Path("backend/app/runtime/admin_ugc_live_media_execution_bridge.py")
api = Path("frontend/src/app/api/admin-creative-media-assets/route.ts")

for path in [bridge, api]:
    if not path.exists():
        raise AssertionError(f"Missing file: {path}")

py_compile.compile(str(bridge), doraise=True)

bridge_text = bridge.read_text(encoding="utf-8", errors="ignore")
api_text = api.read_text(encoding="utf-8", errors="ignore")

for marker in [
    "persist_creative_asset",
    "persisted_asset_records",
    "provider_asset_url",
    "download_url",
]:
    if marker not in bridge_text:
        raise AssertionError(f"Missing bridge marker: {marker}")

for marker in [
    "/admin/persisted-creative-assets",
    "x-actor-role",
    "owner_admin",
    "ADMIN_TOKEN",
]:
    if marker not in api_text:
        raise AssertionError(f"Missing frontend API marker: {marker}")

print("UGC_MEDIA_BRIDGE_PERSIST_ASSETS_PASSED")
'''

def backup(path: Path):
    if path.exists():
        dest = BACKUP / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

def main():
    BACKUP.mkdir(parents=True, exist_ok=True)

    backup(BRIDGE)
    backup(FRONTEND_API)

    text = BRIDGE.read_text(encoding="utf-8", errors="ignore")

    if "persist_creative_asset" not in text:
        import_marker = "def _now() -> str:"
        import_block = '''try:
    from backend.app.runtime.creative_asset_persistence_bridge import persist_creative_asset
except Exception:
    persist_creative_asset = None


'''
        text = text.replace(import_marker, import_block + import_marker, 1)

    old_block = '''    media_assets_created = bool(
        voice_result.get("audio_saved") or video_result.get("video_saved")
    )

    return {
        "success": True,'''

    new_block = '''    media_assets_created = bool(
        voice_result.get("audio_saved") or video_result.get("video_saved")
    )

    persisted_asset_records = []

    if persist_creative_asset is not None:
        if voice_result.get("audio_saved"):
            persisted_asset_records.append(
                persist_creative_asset(
                    {
                        "provider": "elevenlabs",
                        "asset_type": "audio",
                        "test_label": voice_result.get("test_label") or f"{test_label}_voiceover",
                        "provider_asset_id": voice_result.get("generation_id") or voice_result.get("task_id"),
                        "provider_asset_url": voice_result.get("audio_url") or voice_result.get("audio_path"),
                        "preview_url": voice_result.get("audio_url") or voice_result.get("audio_path"),
                        "download_url": voice_result.get("audio_url") or voice_result.get("audio_path"),
                    }
                )
            )

        if video_result.get("video_saved") or video_result.get("video_url_preview") or video_result.get("video_url"):
            persisted_asset_records.append(
                persist_creative_asset(
                    {
                        "provider": "runway",
                        "asset_type": "video",
                        "test_label": video_result.get("test_label") or f"{test_label}_runway_video",
                        "provider_asset_id": video_result.get("task_id") or video_result.get("video_id") or video_result.get("generation_id"),
                        "provider_asset_url": video_result.get("video_url") or video_result.get("video_url_preview") or video_result.get("video_path"),
                        "preview_url": video_result.get("video_url_preview") or video_result.get("video_url") or video_result.get("video_path"),
                        "download_url": video_result.get("video_url") or video_result.get("video_path"),
                    }
                )
            )

    return {
        "success": True,'''

    if old_block not in text:
        raise RuntimeError("Could not find media_assets_created return block in UGC bridge")

    text = text.replace(old_block, new_block, 1)

    insert_after = '''        "video_url_preview": video_result.get("video_url_preview"),'''
    if '"persisted_asset_records": persisted_asset_records,' not in text:
        text = text.replace(
            insert_after,
            insert_after + '''
        "persisted_asset_records": persisted_asset_records,
        "persisted_asset_count": len(persisted_asset_records),''',
            1,
        )

    BRIDGE.write_text(text, encoding="utf-8", newline="\n")
    FRONTEND_API.write_text(FRONTEND_API_CONTENT, encoding="utf-8", newline="\n")
    TEST.write_text(TEST_CONTENT, encoding="utf-8", newline="\n")

    print("UGC_MEDIA_BRIDGE_PERSIST_ASSETS_PATCHED")
    print(f"Backup: {BACKUP}")
    print(f"Updated: {BRIDGE}")
    print(f"Updated: {FRONTEND_API}")
    print(f"Created: {TEST}")

if __name__ == "__main__":
    main()