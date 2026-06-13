from pathlib import Path
from datetime import datetime

backup_dir = Path("backups") / f"universal_status_ignore_readiness_payload_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

# Patch client-facing universal status route to skip generic readiness payloads.
p = Path("frontend/src/app/api/universal-complete-media-status/route.ts")
s = p.read_text(encoding="utf-8")
(backup_dir / "universal-complete-media-status.route.ts").write_text(s, encoding="utf-8")

helper = '''
function isGenericReadinessPayload(data: any, jobId: string) {
  if (!data || typeof data !== "object") return false;
  const returnedJobId = String(data.job_id || data.media_job_id || data.id || "");
  if (returnedJobId && returnedJobId === jobId) return false;

  return Boolean(
    data.universal_complete_media_workflow_ready === true &&
    Array.isArray(data.supported_controls) &&
    !returnedJobId
  );
}
'''

if "function isGenericReadinessPayload" not in s:
    s = s.replace("function decorateMediaAssetUrls(data: any) {", helper + "\nfunction decorateMediaAssetUrls(data: any) {", 1)

old = '''      return NextResponse.json(decorateMediaAssetUrls(data), { status: response.status });
'''
new = '''      if (isGenericReadinessPayload(data, jobId)) {
        lastError = "Backend returned generic universal media readiness instead of job status.";
        continue;
      }

      return NextResponse.json(decorateMediaAssetUrls(data), { status: response.status });
'''

if old not in s:
    raise SystemExit("Could not find universal status return anchor.")

s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")

# Patch admin universal GET to forward job_id and reject generic readiness as job status.
p = Path("frontend/src/app/api/admin-universal-complete-media/route.ts")
s = p.read_text(encoding="utf-8")
(backup_dir / "admin-universal-complete-media.route.ts").write_text(s, encoding="utf-8")

helper = '''
function isGenericReadinessPayload(data: any, jobId: string) {
  if (!data || typeof data !== "object") return false;
  const returnedJobId = String(data.job_id || data.media_job_id || data.id || "");
  if (returnedJobId && returnedJobId === jobId) return false;

  return Boolean(
    data.universal_complete_media_workflow_ready === true &&
    Array.isArray(data.supported_controls) &&
    !returnedJobId
  );
}
'''

if "function isGenericReadinessPayload" not in s:
    s = s.replace("function safeTimeoutResponse(jobId: string, route: string, message: string) {", helper + "\nfunction safeTimeoutResponse(jobId: string, route: string, message: string) {", 1)

old = '''    return NextResponse.json(data, { status: response.status });
'''
new = '''    if (jobId && isGenericReadinessPayload(data, jobId)) {
      return NextResponse.json(
        {
          success: false,
          status: "job_status_not_returned",
          job_id: jobId,
          message: "Backend returned universal media workflow readiness instead of the requested job status.",
          backend_status_available: true,
          polling_required: true,
          customer_safe: true,
          credential_values_exposed: false,
          internal_config_exposed: false,
        },
        { status: 202 }
      );
    }

    return NextResponse.json(data, { status: response.status });
'''

if old not in s:
    raise SystemExit("Could not find admin universal GET return anchor.")

s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")

print("UNIVERSAL_STATUS_READINESS_PAYLOAD_FILTERED")
print(f"Backup: {backup_dir}")
print("Updated frontend/src/app/api/universal-complete-media-status/route.ts")
print("Updated frontend/src/app/api/admin-universal-complete-media/route.ts")