from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"admin_activation_governance_panel_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

page_path = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
test_path = ROOT / "test_admin_activation_governance_panel.py"

backup = BACKUP_DIR / page_path.relative_to(ROOT)
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(page_path.read_text(encoding="utf-8"), encoding="utf-8")

text = page_path.read_text(encoding="utf-8")

nav_old = '"Billing"]'
nav_new = '"Billing", "Activation Governance"]'

if nav_old in text and "Activation Governance" not in text:
    text = text.replace(nav_old, nav_new, 1)

state_marker = "  const registryTotal = clientRegistrySummary?.total || clientRegistrySummary?.tenant_count || clientRegistry.length || 0;\n"
state_insert = '''
  const [activationGovernance, setActivationGovernance] = useState<any>(null);

  async function loadActivationGovernance() {
    try {
      const response = await fetch("/api/admin-activation-governance/summary", {
        method: "GET",
        credentials: "include",
      });
      const data = await response.json();
      setActivationGovernance(data);
    } catch {
      setActivationGovernance({
        success: false,
        message: "Activation governance summary unavailable.",
        credential_values_exposed: false,
        customer_safe: true,
      });
    }
  }

'''

if state_marker not in text:
    raise RuntimeError("Could not find registryTotal marker.")

if "loadActivationGovernance" not in text:
    text = text.replace(state_marker, state_marker + state_insert, 1)

effect_marker = "  return (\n    <main className=\"admin-v2\">"
effect_insert = '''
  useEffect(() => {
    loadActivationGovernance();
  }, []);

'''

if effect_marker not in text:
    raise RuntimeError("Could not find return marker.")

if "loadActivationGovernance();" not in text:
    text = text.replace(effect_marker, effect_insert + effect_marker, 1)

panel_marker = '''        <div className="topRight">
          <span className="runtime"><i /> Runtime: {runtimeStatus}</span>
          <span className="clock">{clock}</span>
          <span className="avatar">OW</span>
        </div>
      </div>
'''

panel_insert = '''        <div className="topRight">
          <span className="runtime"><i /> Runtime: {runtimeStatus}</span>
          <span className="clock">{clock}</span>
          <span className="avatar">OW</span>
        </div>
      </div>

      <section className="card" style={{ marginTop: 18 }}>
        <div className="cardHeader">
          <div>
            <h2>Activation Governance</h2>
            <p>Owner visibility for activation locks, entitlement hydration, blocked changes, and review requirements.</p>
          </div>
          <button className="secondaryBtn" onClick={loadActivationGovernance}>
            Refresh
          </button>
        </div>

        <div className="metricsGrid">
          <div className="metric">
            <span>Activation events</span>
            <strong>{activationGovernance?.summary?.activation_ledger_event_count ?? 0}</strong>
          </div>
          <div className="metric">
            <span>Execution decisions</span>
            <strong>{activationGovernance?.summary?.execution_decision_event_count ?? 0}</strong>
          </div>
          <div className="metric">
            <span>Blocked decisions</span>
            <strong>{activationGovernance?.summary?.blocked_execution_decision_count ?? 0}</strong>
          </div>
          <div className="metric">
            <span>Owner review required</span>
            <strong>{activationGovernance?.summary?.owner_admin_review_required_count ?? 0}</strong>
          </div>
        </div>

        <div className="statusList" style={{ marginTop: 16 }}>
          <div>
            <strong>Runtime entitlement hydration</strong>
            <span>{activationGovernance?.summary?.runtime_entitlement_hydration_ready ? "READY" : "PENDING"}</span>
          </div>
          <div>
            <strong>Client execution limited to activated agents</strong>
            <span>{activationGovernance?.summary?.client_execution_limited_to_activated_agents ? "ENFORCED" : "CHECK"}</span>
          </div>
          <div>
            <strong>Owner/admin unrestricted access</strong>
            <span>{activationGovernance?.summary?.owner_admin_unrestricted_access_preserved ? "PRESERVED" : "CHECK"}</span>
          </div>
          <div>
            <strong>Credential exposure</strong>
            <span>{activationGovernance?.credential_values_exposed === false ? "FALSE" : "CHECK"}</span>
          </div>
        </div>
      </section>
'''

if panel_marker not in text:
    raise RuntimeError("Could not find topbar marker.")

if "Activation Governance</h2>" not in text:
    text = text.replace(panel_marker, panel_insert, 1)

page_path.write_text(text, encoding="utf-8")

test_path.write_text(
'''from pathlib import Path

text = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

assert "Activation Governance" in text
assert "/api/admin-activation-governance/summary" in text
assert "loadActivationGovernance" in text
assert "activation_ledger_event_count" in text
assert "blocked_execution_decision_count" in text
assert "owner_admin_review_required_count" in text
assert "credential_values_exposed" in text

print("ADMIN_ACTIVATION_GOVERNANCE_PANEL_TESTS_PASSED")
print("panel_present", "Activation Governance" in text)
print("summary_api_wired", "/api/admin-activation-governance/summary" in text)
print("credential_marker", "credential_values_exposed" in text)
''',
encoding="utf-8"
)

print("ADMIN_ACTIVATION_GOVERNANCE_PANEL_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {page_path}")
print(f"Created/updated: {test_path}")