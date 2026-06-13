from pathlib import Path
from datetime import datetime

p = Path("backend/app/main.py")
s = p.read_text(encoding="utf-8")

backup_dir = Path("backups") / f"backend_universal_status_job_lookup_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "backend_app_main.py").write_text(s, encoding="utf-8")

old_middleware = '''        if path == "/admin/universal-complete-media-status" and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import universal_complete_media_status

            return JSONResponse(content=universal_complete_media_status())
'''

new_middleware = '''        if path == "/admin/universal-complete-media-status" and request.method.upper() == "GET":
            from backend.app.runtime.direct_media_provider_execution_runtime import (
                get_direct_media_provider_job_status,
                universal_complete_media_status,
            )

            job_id = str(request.query_params.get("job_id") or "").strip()
            if job_id:
                job = get_direct_media_provider_job_status(job_id)
                if job and job.get("status") != "not_found":
                    return JSONResponse(content={
                        **job,
                        "universal_complete_media_status_lookup": True,
                        "direct_media_provider_execution": False,
                        "customer_safe": True,
                        "credential_values_exposed": False,
                    })

                return JSONResponse(
                    status_code=202,
                    content={
                        "success": False,
                        "status": "job_status_not_found",
                        "job_id": job_id,
                        "message": "Universal complete media job status was not found in the active runtime store.",
                        "polling_required": True,
                        "universal_complete_media_status_lookup": True,
                        "customer_safe": True,
                        "credential_values_exposed": False,
                    },
                )

            return JSONResponse(content=universal_complete_media_status())
'''

if old_middleware not in s:
    raise SystemExit("Could not find middleware universal status block.")

s = s.replace(old_middleware, new_middleware, 1)

old_route = '''@app.get("/admin/universal-complete-media-status")
def admin_universal_complete_media_status() -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import universal_complete_media_status

    return universal_complete_media_status()
'''

new_route = '''@app.get("/admin/universal-complete-media-status")
def admin_universal_complete_media_status(job_id: str = "") -> Dict[str, object]:
    from backend.app.runtime.direct_media_provider_execution_runtime import (
        get_direct_media_provider_job_status,
        universal_complete_media_status,
    )

    safe_job_id = str(job_id or "").strip()
    if safe_job_id:
        job = get_direct_media_provider_job_status(safe_job_id)
        if job and job.get("status") != "not_found":
            return {
                **job,
                "universal_complete_media_status_lookup": True,
                "direct_media_provider_execution": False,
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        return {
            "success": False,
            "status": "job_status_not_found",
            "job_id": safe_job_id,
            "message": "Universal complete media job status was not found in the active runtime store.",
            "polling_required": True,
            "universal_complete_media_status_lookup": True,
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    return universal_complete_media_status()
'''

if old_route not in s:
    raise SystemExit("Could not find decorated universal status route block.")

s = s.replace(old_route, new_route, 1)

p.write_text(s, encoding="utf-8")

print("BACKEND_UNIVERSAL_COMPLETE_MEDIA_STATUS_JOB_LOOKUP_FIXED")
print(f"Backup: {backup_dir}")
print("Updated: backend/app/main.py")