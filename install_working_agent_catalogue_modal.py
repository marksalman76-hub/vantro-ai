from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

anchor = """
      {/* HASH_MEDIA_PREVIEW_POPUP_V1 */}
"""

modal = """
      {showEnterpriseCatalogueModal ? (
        <div
          onClick={() => setShowEnterpriseCatalogueModal(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(2,6,23,.82)",
            zIndex: 99999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "min(1100px, 95vw)",
              maxHeight: "85vh",
              overflowY: "auto",
              borderRadius: 24,
              background: "#081028",
              border: "1px solid rgba(129,140,248,.28)",
              padding: 28,
              boxShadow: "0 30px 80px rgba(0,0,0,.55)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: 24,
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: 12,
                    letterSpacing: ".18em",
                    textTransform: "uppercase",
                    color: "#818cf8",
                    fontWeight: 900,
                    marginBottom: 8,
                  }}
                >
                  Full Agent Catalogue
                </div>

                <div
                  style={{
                    fontSize: 28,
                    fontWeight: 900,
                    color: "#fff",
                  }}
                >
                  Available AI Workforce Agents
                </div>
              </div>

              <button
                onClick={() => setShowEnterpriseCatalogueModal(false)}
                style={{
                  border: 0,
                  borderRadius: 999,
                  padding: "10px 16px",
                  background: "#4f46e5",
                  color: "#fff",
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                Close
              </button>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))",
                gap: 14,
              }}
            >
              {visibleAgentCatalogue.map((agentId) => (
                <div
                  key={agentId}
                  style={{
                    border: "1px solid rgba(129,140,248,.22)",
                    borderRadius: 18,
                    padding: 18,
                    background: "rgba(15,23,42,.92)",
                  }}
                >
                  <div
                    style={{
                      color: "#fff",
                      fontWeight: 800,
                      fontSize: 15,
                      marginBottom: 8,
                    }}
                  >
                    {getAgentDisplayName(agentId)}
                  </div>

                  <div
                    style={{
                      color: "#94a3b8",
                      fontSize: 13,
                      lineHeight: 1.6,
                    }}
                  >
                    Enterprise-grade governed execution agent available in your active workspace deployment.
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}

"""

if anchor not in text:
    raise SystemExit("Modal anchor not found")

text = text.replace(anchor, modal + "\n" + anchor, 1)

p.write_text(text, encoding="utf-8")

print("WORKING_AGENT_CATALOGUE_MODAL_INSTALLED")