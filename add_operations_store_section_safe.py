from pathlib import Path

ROOT = Path.cwd()
ADMIN = ROOT / "frontend/src/app/admin/page.tsx"

text = ADMIN.read_text(encoding="utf-8")
original = text

billing_marker = '''          <div id="admin-billing">
            <Panel title="Billing & Deployment" subtitle="Subscription, Stripe and deployment readiness.">'''

operations_section = '''          <div id="admin-operations-store">
            <Panel title="Operations Store" subtitle="Refunds, industry packs, and tenant-safe learning vault.">
              <div className="reviewRows">
                <div><span>Refund requests</span><b>{refundRequests.length}</b></div>
                <div><span>Industry packs</span><b>{industryPacks.length}</b></div>
                <div><span>Learning records</span><b>{learningVaultRecords.length}</b></div>
              </div>
              <button className="ghost full" onClick={loadOperationsStorePanels} disabled={operationsStoreBusy}>
                {operationsStoreBusy ? "Refreshing..." : "Refresh operations store"}
              </button>
            </Panel>
          </div>

''' + billing_marker

if 'id="admin-operations-store"' not in text:
    if billing_marker not in text:
        raise RuntimeError("Billing marker not found")
    text = text.replace(billing_marker, operations_section, 1)

if text == original:
    print("NO_CHANGE_OPERATIONS_STORE_SECTION_ALREADY_PRESENT")
else:
    ADMIN.write_text(text, encoding="utf-8", newline="\n")
    print("OPERATIONS_STORE_SECTION_ADDED")