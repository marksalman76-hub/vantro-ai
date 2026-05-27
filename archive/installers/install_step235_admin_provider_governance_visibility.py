from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
ADMIN_RUNTIME = ROOT / "frontend" / "src" / "app" / "api" / "admin-runtime" / "route.ts"
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_step235_admin_provider_governance_visibility_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file in [ADMIN_RUNTIME, ADMIN_PAGE, TEST]:
    if file.exists():
        backup = BACKUPS / f"{file.stem}_before_step235_{timestamp}{file.suffix}"
        backup.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

runtime_text = ADMIN_RUNTIME.read_text(encoding="utf-8")

old = '''  const health = await safeFetch("/health");

  return NextResponse.json({
    success: true,
    generated_at: new Date().toISOString(),
    health,
'''

new = '''  const health = await safeFetch("/health");
  const providerReadiness = await safeFetch("/admin/provider-readiness");
  const providerAudit = await safeFetch("/admin/provider-execution-audit?limit=10");
  const openaiSdkReadiness = await safeFetch("/admin/openai-sdk-readiness");
  const liveLlmDashboard = await safeFetch("/admin/live-llm-readiness-dashboard");
  const liveLlmControl = await safeFetch("/admin/live-llm-control");
  const operationalDashboard = await safeFetch("/admin/operational-dashboard");
  const databaseReadiness = await safeFetch("/admin/database-readiness");
  const billingReadiness = await safeFetch("/admin/billing/readiness");

  return NextResponse.json({
    success: true,
    generated_at: new Date().toISOString(),
    health,
    provider_governance: {
      provider_readiness: providerReadiness,
      provider_audit: providerAudit,
      openai_sdk_readiness: openaiSdkReadiness,
      live_llm_dashboard: liveLlmDashboard,
      live_llm_control: liveLlmControl,
      operational_dashboard: operationalDashboard,
      database_readiness: databaseReadiness,
      billing_readiness: billingReadiness,
    },
'''

if old not in runtime_text:
    raise RuntimeError("Expected admin-runtime health block not found.")

runtime_text = runtime_text.replace(old, new)

runtime_text = runtime_text.replace(
    '''      regression_status: "passing",
    },
''',
    '''      regression_status: "passing",
      provider_governance_visibility: "active",
      provider_audit_visibility: "active",
      live_llm_control_visibility: "active",
      deployment_readiness_visibility: "active",
    },
'''
)

ADMIN_RUNTIME.write_text(runtime_text, encoding="utf-8")

page_text = ADMIN_PAGE.read_text(encoding="utf-8")

page_text = page_text.replace(
    '''  health?: any;
};''',
    '''  health?: any;
  provider_governance?: any;
};'''
)

insert_after = '''            <div
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

              <div
                style={{
                  marginTop: 18,
                }}
              >
                <JsonBlock value={runtime.health} />
              </div>
            </div>
'''

provider_panel = '''            <div
              style={{
                marginTop: 34,
                background: "rgba(15,23,42,.82)",
                border: "1px solid rgba(148,163,184,.14)",
                borderRadius: 22,
                padding: 24,
              }}
            >
              <h2 style={{ fontSize: 28 }}>
                Live Provider Governance
              </h2>

              <p
                style={{
                  color: "#94a3b8",
                  lineHeight: 1.7,
                  marginTop: 8,
                }}
              >
                Admin-only visibility for provider readiness, OpenAI SDK status,
                live LLM controls, audit logs, database readiness, and billing readiness.
                Secret values and internal prompts remain hidden.
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
                  label="Provider Readiness"
                  value={runtime.provider_governance?.provider_readiness?.ok ? "Available" : "Unavailable"}
                />

                <StatCard
                  label="OpenAI SDK"
                  value={runtime.provider_governance?.openai_sdk_readiness?.ok ? "Ready Check Available" : "Unavailable"}
                />

                <StatCard
                  label="Live LLM Control"
                  value={runtime.provider_governance?.live_llm_control?.ok ? "Governed" : "Unavailable"}
                />

                <StatCard
                  label="Provider Audit Events"
                  value={runtime.provider_governance?.provider_audit?.data?.count || 0}
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
                  <h3>Provider Readiness</h3>
                  <JsonBlock value={runtime.provider_governance?.provider_readiness?.data || runtime.provider_governance?.provider_readiness} />
                </div>

                <div>
                  <h3>Live LLM Dashboard</h3>
                  <JsonBlock value={runtime.provider_governance?.live_llm_dashboard?.data || runtime.provider_governance?.live_llm_dashboard} />
                </div>

                <div>
                  <h3>Provider Audit</h3>
                  <JsonBlock value={runtime.provider_governance?.provider_audit?.data || runtime.provider_governance?.provider_audit} />
                </div>

                <div>
                  <h3>Deployment / Data Readiness</h3>
                  <JsonBlock value={{
                    database: runtime.provider_governance?.database_readiness?.data || runtime.provider_governance?.database_readiness,
                    billing: runtime.provider_governance?.billing_readiness?.data || runtime.provider_governance?.billing_readiness,
                    operational: runtime.provider_governance?.operational_dashboard?.data || runtime.provider_governance?.operational_dashboard,
                  }} />
                </div>
              </div>
            </div>
'''

if insert_after not in page_text:
    raise RuntimeError("Expected backend health panel not found in admin page.")

page_text = page_text.replace(insert_after, insert_after + "\n" + provider_panel)

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

governance = data.get("provider_governance") or {}

combined_text = json.dumps(data).lower()

checks = {
    "admin_runtime_success": data.get("success") is True,
    "provider_governance_present": isinstance(governance, dict),
    "provider_readiness_present": "provider_readiness" in governance,
    "provider_audit_present": "provider_audit" in governance,
    "openai_sdk_readiness_present": "openai_sdk_readiness" in governance,
    "live_llm_dashboard_present": "live_llm_dashboard" in governance,
    "live_llm_control_present": "live_llm_control" in governance,
    "database_readiness_present": "database_readiness" in governance,
    "billing_readiness_present": "billing_readiness" in governance,
    "no_secret_values_exposed": all(secret not in combined_text for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_235_ADMIN_PROVIDER_GOVERNANCE_VISIBILITY_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    print(json.dumps(data, indent=2))
    raise SystemExit(1)

print("STEP_235_ADMIN_PROVIDER_GOVERNANCE_VISIBILITY_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_235_ADMIN_PROVIDER_GOVERNANCE_VISIBILITY_INSTALLED")
print(f"Updated: {ADMIN_RUNTIME}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created/updated: {TEST}")
print("STEP_235_OK")