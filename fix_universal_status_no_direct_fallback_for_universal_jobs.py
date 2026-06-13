from pathlib import Path
from datetime import datetime

p = Path("frontend/src/app/api/universal-complete-media-status/route.ts")
s = p.read_text(encoding="utf-8")

backup_dir = Path("backups") / f"universal_status_no_direct_fallback_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "universal-complete-media-status.route.ts").write_text(s, encoding="utf-8")

old = '''  const statusUrls = [
    `${backendBaseUrl()}/admin/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`,
    `${backendBaseUrl()}/admin/direct-media-provider-job-status/${encodeURIComponent(jobId)}`,
  ];
'''

new = '''  const isUniversalJob = jobId.startsWith("universal_complete_media_job_");

  const statusUrls = isUniversalJob
    ? [
        `${backendBaseUrl()}/admin/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`,
      ]
    : [
        `${backendBaseUrl()}/admin/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`,
        `${backendBaseUrl()}/admin/direct-media-provider-job-status/${encodeURIComponent(jobId)}`,
      ];
'''

if old not in s:
    raise SystemExit("Could not find statusUrls block.")

s = s.replace(old, new, 1)

old = '''  return NextResponse.json(
    {
      success: false,
      status: "status_lookup_timeout",
      job_id: jobId,
      message: "Universal complete media status lookup timed out before a backend response was available.",
      last_error: lastError,
      polling_required: true,
      customer_safe: true,
      credential_values_exposed: false,
      internal_config_exposed: false,
    },
    { status: 202 }
  );
'''

new = '''  return NextResponse.json(
    {
      success: false,
      status: isUniversalJob ? "job_status_not_returned" : "status_lookup_timeout",
      job_id: jobId,
      message: isUniversalJob
        ? "Backend did not return a per-job status for this universal complete media job."
        : "Universal complete media status lookup timed out before a backend response was available.",
      last_error: lastError,
      polling_required: true,
      customer_safe: true,
      credential_values_exposed: false,
      internal_config_exposed: false,
    },
    { status: 202 }
  );
'''

if old not in s:
    raise SystemExit("Could not find final fallback response block.")

s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")

print("UNIVERSAL_STATUS_NO_DIRECT_FALLBACK_FOR_UNIVERSAL_JOBS")
print(f"Updated: {p}")
print(f"Backup: {backup_dir}")