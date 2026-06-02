from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

start = text.find('{visibleAgentCatalogue.map((agentId) => (')
if start == -1:
    raise SystemExit("visibleAgentCatalogue map start not found")

end = text.find('              ))}', start)
if end == -1:
    raise SystemExit("visibleAgentCatalogue map end not found")

block = text[start:end + len('              ))}')]

new_block = '''{visibleAgentCatalogue.map((agentId) => (
                <button
                  type="button"
                  key={agentId}
                  onClick={() => {
                    setSelectedAgents([agentId]);
                    setShowEnterpriseCatalogueModal(false);
                    setToastMessage(`${getAgentDisplayName(agentId)} selected.`);
                  }}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    border: "1px solid rgba(129,140,248,.22)",
                    borderRadius: 18,
                    padding: 18,
                    background: selectedAgents.includes(agentId)
                      ? "rgba(79,70,229,.42)"
                      : "rgba(15,23,42,.92)",
                    cursor: "pointer",
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
                </button>
              ))}'''

text = text[:start] + new_block + text[end + len('              ))}'):]

p.write_text(text, encoding="utf-8")
print("CLIENT_CATALOGUE_AGENTS_CLICKABLE_SAFE")