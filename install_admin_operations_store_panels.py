from pathlib import Path

ROOT = Path.cwd()
admin = ROOT / "frontend/src/app/admin/page.tsx"

text = admin.read_text(encoding="utf-8")
original = text

# 1) Add state
state_marker = '''  const [orchestrationBusy, setOrchestrationBusy] = useState(false);
  const [orchestrationResult, setOrchestrationResult] = useState<any>(null);

  const [clock, setClock] = useState("--:--:--");
'''
state_insert = '''  const [orchestrationBusy, setOrchestrationBusy] = useState(false);
  const [orchestrationResult, setOrchestrationResult] = useState<any>(null);
  const [refundRequests, setRefundRequests] = useState<any[]>([]);
  const [industryPacks, setIndustryPacks] = useState<any[]>([]);
  const [learningVaultRecords, setLearningVaultRecords] = useState<any[]>([]);
  const [operationsStoreBusy, setOperationsStoreBusy] = useState(false);

  const [clock, setClock] = useState("--:--:--");
'''
text = text.replace(state_marker, state_insert)

# 2) Add functions before first useEffect that loads runtime
function_marker = '''  useEffect(() => {
    loadRuntime();
    loadClientRegistry();
    loadOrchestrationDashboard();
    loadActionExecutionHistory();
  }, []);
'''
function_insert = '''  async function loadOperationsStorePanels() {
    setOperationsStoreBusy(true);
    try {
      const [refundRes, packsRes, vaultRes] = await Promise.all([
        fetch("/api/admin-billing-refund-requests?limit=10", { cache: "no-store", headers: { "x-actor-role": "owner_admin" } }),
        fetch("/api/admin-industry-agent-store-packs?limit=10", { cache: "no-store", headers: { "x-actor-role": "owner_admin" } }),
        fetch("/api/admin-learning-vault-records?limit=10", { cache: "no-store", headers: { "x-actor-role": "owner_admin" } }),
      ]);
      const refundData = await refundRes.json().catch(() => ({}));
      const packsData = await packsRes.json().catch(() => ({}));
      const vaultData = await vaultRes.json().catch(() => ({}));
      setRefundRequests(Array.isArray(refundData?.refunds) ? refundData.refunds : []);
      setIndustryPacks(Array.isArray(packsData?.industry_packs) ? packsData.industry_packs : []);
      setLearningVaultRecords(Array.isArray(vaultData?.learning_records) ? vaultData.learning_records : []);
      showToast("Operations store refreshed.");
    } catch {
      setRefundRequests([]);
      setIndustryPacks([]);
      setLearningVaultRecords([]);
      showToast("Operations store refresh failed.");
    } finally {
      setOperationsStoreBusy(false);
    }
  }

  async function approveRefundRequest(refundId: string) {
    try {
      const response = await fetch("/api/admin-billing-refund-decision", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json", "x-actor-role": "owner_admin" },
        body: JSON.stringify({ refund_id: refundId, decision: "approve", approved_by: "owner_admin", note: "Approved from admin refund queue." }),
      });
      const data = await response.json().catch(() => ({}));
      showToast(data?.success === false ? `Refund approval blocked: ${data?.error || "review required"}` : "Refund approved for execution.");
      loadOperationsStorePanels();
    } catch {
      showToast("Refund approval failed.");
    }
  }

  async function rejectRefundRequest(refundId: string) {
    try {
      const response = await fetch("/api/admin-billing-refund-decision", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json", "x-actor-role": "owner_admin" },
        body: JSON.stringify({ refund_id: refundId, decision: "reject", approved_by: "owner_admin", note: "Rejected from admin refund queue." }),
      });
      const data = await response.json().catch(() => ({}));
      showToast(data?.success === false ? "Refund rejection failed." : "Refund rejected.");
      loadOperationsStorePanels();
    } catch {
      showToast("Refund rejection failed.");
    }
  }

  async function executeRefundRequest(refundId: string, amountCents?: number) {
    try {
      const response = await fetch("/api/admin-billing-refund-execute", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json", "x-actor-role": "owner_admin" },
        body: JSON.stringify({ refund_id: refundId, actor: "owner_admin", amount_cents: amountCents || 0 }),
      });
      const data = await response.json().catch(() => ({}));
      showToast(data?.success === false ? `Refund execution failed: ${data?.error || "review required"}` : "Refund execution completed.");
      loadOperationsStorePanels();
    } catch {
      showToast("Refund execution failed.");
    }
  }

  useEffect(() => {
    loadRuntime();
    loadClientRegistry();
    loadOrchestrationDashboard();
    loadActionExecutionHistory();
    loadOperationsStorePanels();
  }, []);
'''
text = text.replace(function_marker, function_insert)

# 3) Add nav item
text = text.replace(
    'const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing"];',
    'const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing", "Operations Store"];'
)

# 4) Add section map
text = text.replace(
    '"Billing": "admin-billing",',
    '"Billing": "admin-billing",\n      "Operations Store": "admin-operations-store",'
)

# 5) Add panels before Billing section
billing_marker = '''            <div id="admin-billing">
              <Panel title="Billing & Subscription Control" subtitle="Stripe and package automation readiness.">'''
operations_panel = '''            <div id="admin-operations-store">
              <Panel title="Operations Store" subtitle="Owner-only refund queue, industry agent store, and tenant-safe learning vault.">
                <div className="reviewRows">
                  <div><span>Refund requests</span><b>{refundRequests.length}</b></div>
                  <div><span>Industry packs</span><b>{industryPacks.length}</b></div>
                  <div><span>Learning records</span><b>{learningVaultRecords.length}</b></div>
                </div>
                <button className="ghost full" onClick={loadOperationsStorePanels} disabled={operationsStoreBusy}>
                  {operationsStoreBusy ? "Refreshing..." : "Refresh operations store"}
                </button>
              </Panel>

              <div className="grid two">
                <Panel title="Refund Queue" subtitle="Owner-approved refund decisions with usage-policy enforcement.">
                  {refundRequests.length ? refundRequests.slice(0, 6).map((item: any) => (
                    <div className="clientRow" key={item.refund_id}>
                      <strong>{item.customer_email || item.tenant_id || "Refund request"}</strong>
                      <span>{item.status || "pending"}</span>
                      <p>
                        Amount: {item.requested_amount_cents ? `$${(Number(item.requested_amount_cents) / 100).toFixed(2)}` : "—"} ·
                        Used: {item?.usage_verification?.platform_used ? "Yes" : "No"} ·
                        Reason: {item.reason || "Not provided"}
                      </p>
                      <div className="panelActions">
                        <button className="ghost" onClick={() => approveRefundRequest(item.refund_id)}>Approve</button>
                        <button className="warn" onClick={() => rejectRefundRequest(item.refund_id)}>Reject</button>
                        <button className="reactivate" onClick={() => executeRefundRequest(item.refund_id, item.requested_amount_cents)}>Execute</button>
                      </div>
                    </div>
                  )) : (
                    <div className="clientRow">
                      <strong>No refund requests</strong>
                      <p>Refund requests submitted by clients will appear here.</p>
                    </div>
                  )}
                </Panel>

                <Panel title="Industry Agent Store" subtitle="Reusable industry deployment packs for future client deployments.">
                  {industryPacks.length ? industryPacks.slice(0, 6).map((pack: any) => (
                    <div className="clientRow" key={pack.pack_id || pack.industry}>
                      <strong>{pack.display_name || pack.industry || "Industry pack"}</strong>
                      <span>{pack.industry || "industry"}</span>
                      <p>
                        Agents: {(pack.agents || []).length} ·
                        Integrations: {(pack.recommended_integrations || []).join(", ") || "—"}
                      </p>
                    </div>
                  )) : (
                    <div className="clientRow">
                      <strong>No industry packs yet</strong>
                      <p>Create packs through the admin industry store API or capture from approved deployments.</p>
                    </div>
                  )}
                </Panel>
              </div>

              <Panel title="Learning Vault" subtitle="Tenant-safe reusable learning patterns captured from client outcomes.">
                {learningVaultRecords.length ? learningVaultRecords.slice(0, 8).map((record: any) => (
                  <div className="clientRow" key={record.vault_id}>
                    <strong>{String(record.agent_id || "agent").replaceAll("_", " ")}</strong>
                    <span>{record.industry || "general"}</span>
                    <p>{record.tenant_safe_summary || (record.recommended_improvements || []).join(" · ") || "Tenant-safe learning record captured."}</p>
                  </div>
                )) : (
                  <div className="clientRow">
                    <strong>No learning records yet</strong>
                    <p>Approved client-safe learning patterns will appear here for future deployments.</p>
                  </div>
                )}
              </Panel>
            </div>

''' + billing_marker
text = text.replace(billing_marker, operations_panel)

admin.write_text(text, encoding="utf-8")

if text != original:
    print("ADMIN_OPERATIONS_STORE_PANELS_INSTALLED")
else:
    print("NO_CHANGE_ADMIN_OPERATIONS_STORE_PANELS")