from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

anchor_state = '''  const [showEnterpriseCatalogueModal, setShowEnterpriseCatalogueModal] = useState(false);'''

replacement_state = '''  const [showEnterpriseCatalogueModal, setShowEnterpriseCatalogueModal] = useState(false);
  const [clientMounted, setClientMounted] = useState(false);'''

if anchor_state not in text:
    raise SystemExit("catalogue modal state anchor not found")

text = text.replace(anchor_state, replacement_state, 1)

anchor_effect = '''  useEffect(() => {'''

insert_before = '''  useEffect(() => {
    setClientMounted(true);
  }, []);

  if (!clientMounted) {
    return (
      <main
        style={{
          minHeight: "100vh",
          background: "#020617",
          color: "#e5e7eb",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "var(--font-sans, Arial, sans-serif)",
          padding: 24,
        }}
      >
        <div
          style={{
            border: "1px solid rgba(129,140,248,.25)",
            borderRadius: 24,
            background: "rgba(15,23,42,.92)",
            padding: 28,
            maxWidth: 520,
            textAlign: "center",
            boxShadow: "0 24px 80px rgba(0,0,0,.45)",
          }}
        >
          <div style={{ fontSize: 13, letterSpacing: ".16em", textTransform: "uppercase", color: "#818cf8", fontWeight: 900, marginBottom: 10 }}>
            Client workspace
          </div>
          <h1 style={{ margin: 0, fontSize: 28, color: "#fff" }}>Loading governed workspace...</h1>
          <p style={{ margin: "12px 0 0", color: "#94a3b8", lineHeight: 1.6 }}>
            Preparing your client-safe execution environment.
          </p>
        </div>
      </main>
    );
  }

'''

first_effect_index = text.find(anchor_effect)
if first_effect_index == -1:
    raise SystemExit("first useEffect anchor not found")

text = text[:first_effect_index] + insert_before + text[first_effect_index:]

p.write_text(text, encoding="utf-8")
print("CLIENT_HYDRATION_418_MOUNT_GATE_INSTALLED")