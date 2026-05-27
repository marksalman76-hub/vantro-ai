from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ADMIN_RUNTIME = ROOT / "frontend" / "src" / "app" / "api" / "admin-runtime" / "route.ts"
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_step237_admin_operations_visibility_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in [ADMIN_RUNTIME, ADMIN_PAGE, TEST]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step237_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

runtime_text = ADMIN_RUNTIME.read_text(encoding="utf-8")

runtime_text = runtime_text.replace(
    '''  const billingReadiness = await safeFetch("/admin/billing/readiness");
''',
    '''  const billingReadiness = await safeFetch("/admin/billing/readiness");
  const recoverySummary = await safeFetch("/admin/operations/recovery-summary");
  const operationalArtifacts = await safeFetch("/admin/operations/artifacts?limit=12");
'''
)

runtime_text = runtime_text.replace(
    '''      billing_readiness: billingReadiness,
    },
''',
    '''      billing_readiness: billingReadiness,
    },
    operations: {
      recovery_summary: recoverySummary,
      artifacts: operationalArtifacts,
    },
'''
)

ADMIN_RUNTIME.write_text(runtime_text, encoding="utf-8")

page_text = ADMIN_PAGE.read_text(encoding="utf-8")

page_text = page_text.replace(
    '''  provider_governance?: any;
};''',
    '''  provider_governance?: any;
  operations?: any;
};'''
)

insert_before = '''            <div
              style={{
                marginTop: 34,
                background: "rgba(15,23,42,.82)",
                border: "1px solid rgba(148,163,184,.14)",
                borderRadius: 22,
                padding: 24,
              }}
            >
              <h2 style={{ fontSize: 28 }}>
                Backend Health Payload
              </h2>
'''

operations_panel = '''            <div
              style={{
                marginTop: 34,
                background: "rgba(15,23,42,.82)",
                border: "1px solid rgba(148,163,184,.14)",
                borderRadius: 22,
                padding: 24,
              }}
            >
              <h2 style={{ fontSize: 28 }}>
                Operational Recovery & Artifacts
              </h2>

              <p
                style={{
                  color: "#94a3b8",
                  lineHeight: 1.7,
                  marginTop: 8,
                }}
              >
                Admin-only recovery tooling for generated artifacts, execution replay,
                failed execution retry preparation, audit visibility, and production
                recovery workflows.
              </p>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))",
                  gap: 16,
                  marginTop: 20,
                }}
              >
                <StatCard
                  label="Artifact Registry"
                  value={runtime.operations?.artifacts?.data?.count || 0}
                />

                <StatCard
                  label="Replay Controls"
                  value={runtime.operations?.recovery_summary?.data?.execution_recovery?.replay_controls_ready ? "Ready" : "Unavailable"}
                />

                <StatCard
                  label="Retry Controls"
                  value={runtime.operations?.recovery_summary?.data?.execution_recovery?.retry_controls_ready ? "Ready" : "Unavailable"}
                />

                <StatCard
                  label="Preview Sanitisation"
                  value={runtime.operations?.recovery_summary?.data?.artifact_management?.preview_sanitisation_enabled ? "Active" : "Unavailable"}
                />
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit,minmax(460px,1fr))",
                  gap: 20,
                  marginTop: 24,
                }}
              >
                <div>
                  <h3>Recovery Summary</h3>
                  <JsonBlock value={runtime.operations?.recovery_summary?.data || runtime.operations?.recovery_summary} />
                </div>

                <div>
                  <h3>Latest Artifacts</h3>
                  <JsonBlock value={runtime.operations?.artifacts?.data || runtime.operations?.artifacts} />
                </div>
              </div>
            </div>

'''

if insert_before not in page_text:
    raise RuntimeError("Expected backend health payload panel anchor not found.")

page_text = page_text.replace(insert_before, operations_panel + insert_before)

ADMIN_PAGE.write_text(page_text, encoding="utf-8")

TEST.write_text(r'''
import json
import urllib.request

BASE = "http://127.0.0.1:3000"

req = urllib.request.Request(
    BASE + "/api/admin-runtime",
    method="GET",
)

with urllib.request.urlopen(req, timeout=30) as res:
    data = json.loads(res.read().decode("utf-8"))

operations = data.get("operations") or {}
combined = json.dumps(data).lower()

checks = {
    "admin_runtime_success": data.get("success") is True,
    "operations_present": isinstance(operations, dict),
    "recovery_summary_present": "recovery_summary" in operations,
    "artifacts_present": "artifacts" in operations,
    "recovery_summary_ok": operations.get("recovery_summary", {}).get("ok") is True,
    "artifacts_ok": operations.get("artifacts", {}).get("ok") is True,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_237_ADMIN_OPERATIONS_VISIBILITY_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps(data, indent=2))
    raise SystemExit(1)

print("STEP_237_ADMIN_OPERATIONS_VISIBILITY_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_237_ADMIN_OPERATIONS_VISIBILITY_INSTALLED")
print(f"Updated: {ADMIN_RUNTIME}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created/updated: {TEST}")
print("STEP_237_OK")