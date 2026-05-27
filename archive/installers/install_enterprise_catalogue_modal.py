from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_enterprise_catalogue_modal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

src = src.replace(
'''  const [activeAccountPanel, setActiveAccountPanel] = useState("");
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);''',
'''  const [activeAccountPanel, setActiveAccountPanel] = useState("");
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const [showEnterpriseCatalogueModal, setShowEnterpriseCatalogueModal] = useState(false);''',
1,
)

src = src.replace(
'''  const visibleAgentCatalogue = getPackageAgentCatalogue(accountPackage, account?.active_agents);
  const visibleAgentCount = visibleAgentCatalogue.length;
  const packageAgentLimitLabel = getPackageAgentLimitLabel(accountPackage, visibleAgentCount);''',
'''  const visibleAgentCatalogue = getPackageAgentCatalogue(accountPackage, account?.active_agents);
  const visibleAgentCount = visibleAgentCatalogue.length;
  const packageAgentLimitLabel = getPackageAgentLimitLabel(accountPackage, visibleAgentCount);
  const isEnterprisePackage = String(accountPackage || "").toLowerCase().includes("enterprise");
  const inlineVisibleAgentCatalogue = isEnterprisePackage
    ? visibleAgentCatalogue.slice(0, 7)
    : visibleAgentCatalogue;''',
1,
)

src = src.replace(
'''                  {visibleAgentCatalogue.map((agent) => {''',
'''                  {inlineVisibleAgentCatalogue.map((agent) => {''',
1,
)

old_after_agent_list = '''                </div>
              </div>

              <div>
                <div style={labelStyle}>Task</div>'''

new_after_agent_list = '''                </div>

                {isEnterprisePackage ? (
                  <button
                    type="button"
                    onClick={() => setShowEnterpriseCatalogueModal(true)}
                    style={{
                      marginTop: 10,
                      width: "100%",
                      border: "1px solid #d8dcff",
                      background: "#fff",
                      color: "var(--color-brand)",
                      borderRadius: 12,
                      padding: "9px 10px",
                      fontSize: 11.8,
                      fontWeight: 900,
                      cursor: "pointer",
                      boxShadow: "0 8px 20px rgba(15,23,42,.04)",
                    }}
                  >
                    View full catalogue →
                  </button>
                ) : null}
              </div>

              <div>
                <div style={labelStyle}>Task</div>'''

if old_after_agent_list not in src:
    raise SystemExit("ERROR: Could not find agent list closing block.")

src = src.replace(old_after_agent_list, new_after_agent_list, 1)

modal_block = r'''
      {showEnterpriseCatalogueModal ? (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Full enterprise agent catalogue"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 80,
            background: "rgba(15,23,42,0.42)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 18,
          }}
          onClick={() => setShowEnterpriseCatalogueModal(false)}
        >
          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(920px, 96vw)",
              maxHeight: "82vh",
              background: "#fff",
              borderRadius: 24,
              border: "1px solid #e5eaf2",
              boxShadow: "0 30px 90px rgba(15,23,42,.24)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "20px 22px",
                borderBottom: "1px solid #edf1f6",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "space-between",
                gap: 16,
              }}
            >
              <div>
                <div style={{ color: "var(--color-brand)", fontSize: 11.8, fontWeight: 900, letterSpacing: 0.9, textTransform: "uppercase" }}>
                  Enterprise catalogue
                </div>
                <h3 style={{ ...cardTitle, marginTop: 6 }}>Full governed workforce</h3>
                <p style={{ ...mutedText, margin: "6px 0 0" }}>
                  View all available enterprise agents while keeping the main workspace compact.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowEnterpriseCatalogueModal(false)}
                style={{
                  border: "1px solid #e5eaf2",
                  background: "#fff",
                  borderRadius: 12,
                  padding: "8px 11px",
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                Close
              </button>
            </div>

            <div style={{ padding: 18, maxHeight: "62vh", overflowY: "auto" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 10 }}>
                {visibleAgentCatalogue.map((agent) => {
                  const active = selectedAgents.includes(agent);
                  const agentName = getAgentDisplayName(agent);
                  return (
                    <button
                      key={`enterprise-${agentName}`}
                      type="button"
                      onClick={() => toggleAgent(agent)}
                      style={{
                        border: active ? "1px solid rgba(37, 99, 235, 0.34)" : "1px solid rgba(15, 23, 42, 0.10)",
                        background: active ? "linear-gradient(135deg,#eff6ff,#ffffff)" : "#ffffff",
                        color: active ? "var(--color-brand)" : "var(--color-dark)",
                        padding: "10px 11px",
                        borderRadius: 14,
                        cursor: "pointer",
                        textAlign: "left",
                        fontSize: 12,
                        fontWeight: 800,
                        display: "grid",
                        gridTemplateColumns: "18px minmax(0,1fr)",
                        gap: 9,
                        alignItems: "center",
                        boxShadow: active ? "0 10px 30px rgba(37,99,235,0.10)" : "0 1px 2px rgba(15,23,42,0.03)",
                      }}
                    >
                      <span
                        style={{
                          width: 14,
                          height: 14,
                          borderRadius: 999,
                          border: active ? "none" : "1.5px solid rgba(79,70,229,.45)",
                          background: active ? "var(--color-brand)" : "#ffffff",
                          color: "#fff",
                          display: "inline-flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: 9,
                          fontWeight: 900,
                        }}
                      >
                        {active ? "✓" : ""}
                      </span>
                      <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {agentName}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      ) : null}
'''

insert_before = '''      {showRejectModal ? ('''
if insert_before not in src:
    raise SystemExit("ERROR: Could not find modal insertion point.")

src = src.replace(insert_before, modal_block + "\n" + insert_before, 1)

PAGE.write_text(src, encoding="utf-8")

print("ENTERPRISE_CATALOGUE_MODAL_INSTALLED")
print(f"Backup: {backup}")
print("Enterprise modal state:", "showEnterpriseCatalogueModal" in src)
print("Inline enterprise slice:", "inlineVisibleAgentCatalogue" in src)
print("View full catalogue button:", "View full catalogue" in src)
print("Right column locked:", src.count("Live execution flow") == 1 and src.count("Business profile applied") == 1 and src.count("Governed execution, every time.") == 1)
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))