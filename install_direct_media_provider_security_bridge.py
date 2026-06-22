from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "backend" / "app" / "main.py"
TEST = ROOT / "test_direct_media_provider_security_bridge.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"direct_media_provider_security_bridge_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

(BACKUP_DIR / "main.py").write_text(MAIN.read_text(encoding="utf-8"), encoding="utf-8")

main = MAIN.read_text(encoding="utf-8")

bridge = r'''

# DIRECT_MEDIA_PROVIDER_SECURITY_BRIDGE_V1
@app.middleware("http")
async def direct_media_provider_security_bridge_middleware(request, call_next):
    path = request.url.path.rstrip("/")
    is_direct_media_path = (
        path == "/admin/direct-media-provider-status"
        or path == "/admin/direct-media-provider-execute"
        or path.startswith("/admin/direct-media-provider-job-status/")
    )

    if not is_direct_media_path:
        return await call_next(request)

    from fastapi.responses import JSONResponse

    x_actor_role = request.headers.get("x-actor-role")
    x_admin_token = request.headers.get("x-admin-token")
    authorization = request.headers.get("authorization") or request.headers.get("Authorization")

    try:
        authorized = _admin_media_job_authorized(
            x_actor_role=x_actor_role,
            x_admin_token=x_admin_token,
            authorization=authorization,
        )
    except Exception:
        authorized = False

    if not authorized:
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": "admin_only",
                "message": "Direct media provider execution requires owner/admin authorization.",
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )

    try:
        if path == "/admin/direct-media-provider-status" and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import direct_media_provider_execution_status

            return JSONResponse(content=direct_media_provider_execution_status())

        if path == "/admin/direct-media-provider-execute" and request.method.upper() == "POST":
            from backend.app.runtime.direct_media_provider_execution_runtime import execute_direct_media_provider_job

            try:
                payload = await request.json()
            except Exception:
                payload = {}

            return JSONResponse(content=execute_direct_media_provider_job(payload))

        if path.startswith("/admin/direct-media-provider-job-status/") and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import get_direct_media_provider_job_status

            job_id = path.rsplit("/", 1)[-1]
            return JSONResponse(content=get_direct_media_provider_job_status(job_id))

        return JSONResponse(
            status_code=405,
            content={
                "success": False,
                "error": "method_not_allowed",
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "direct_media_provider_bridge_failed",
                "message": str(error)[:800],
                "customer_safe": True,
                "credential_values_exposed": False,
            },
        )
'''

if "DIRECT_MEDIA_PROVIDER_SECURITY_BRIDGE_V1" not in main:
    main = main.rstrip() + "\n" + bridge + "\n"

MAIN.write_text(main, encoding="utf-8")

TEST.write_text(
    r'''from backend.app.runtime.direct_media_provider_execution_runtime import direct_media_provider_execution_status


def test_direct_media_provider_status_runtime_available():
    result = direct_media_provider_execution_status()
    assert result["success"] is True, result
    assert result["direct_media_provider_execution_ready"] is True, result
    assert result["credential_values_exposed"] is False, result
    assert "runway" in result["supported_video_providers"], result
    assert "elevenlabs" in result["supported_audio_providers"], result


if __name__ == "__main__":
    test_direct_media_provider_status_runtime_available()
    print("DIRECT_MEDIA_PROVIDER_SECURITY_BRIDGE_TEST_PASSED")
''',
    encoding="utf-8",
)

print("DIRECT_MEDIA_PROVIDER_SECURITY_BRIDGE_INSTALLED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {MAIN}")
print(f"Created: {TEST}")
