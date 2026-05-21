from pathlib import Path

base = Path("frontend/src/app/client/billing")
base.mkdir(parents=True, exist_ok=True)

page = '''export default function BillingPage() {
  return (
    <main style={{ minHeight: "100vh", padding: 32, fontFamily: "Inter, system-ui, Arial", background: "#f8fafc", color: "#101828" }}>
      <section style={{ maxWidth: 760, margin: "0 auto", background: "#fff", border: "1px solid #e5e7eb", borderRadius: 24, padding: 32, boxShadow: "0 18px 50px rgba(15,23,42,.08)" }}>
        <div style={{ color: "#635BFF", fontWeight: 900, letterSpacing: ".08em", fontSize: 12 }}>BILLING</div>
        <h1 style={{ fontSize: 34, margin: "10px 0 8px" }}>Billing status</h1>
        <p style={{ color: "#667085", lineHeight: 1.6 }}>Your billing session has been processed. Please continue to your client workspace or contact support if you need help.</p>
        <a href="/client" style={{ display: "inline-block", marginTop: 18, background: "#635BFF", color: "#fff", textDecoration: "none", padding: "13px 18px", borderRadius: 14, fontWeight: 900 }}>Go to workspace</a>
      </section>
    </main>
  );
}
'''

success = '''export default function BillingSuccessPage() {
  return (
    <main style={{ minHeight: "100vh", padding: 32, fontFamily: "Inter, system-ui, Arial", background: "#f8fafc", color: "#101828" }}>
      <section style={{ maxWidth: 760, margin: "0 auto", background: "#fff", border: "1px solid #dcfce7", borderRadius: 24, padding: 32, boxShadow: "0 18px 50px rgba(15,23,42,.08)" }}>
        <div style={{ color: "#16a34a", fontWeight: 900, letterSpacing: ".08em", fontSize: 12 }}>PAYMENT SUCCESSFUL</div>
        <h1 style={{ fontSize: 34, margin: "10px 0 8px" }}>Your subscription is being activated</h1>
        <p style={{ color: "#667085", lineHeight: 1.6 }}>Payment was successful. Your account, selected agents, and activation access will be prepared according to your plan.</p>
        <a href="/login" style={{ display: "inline-block", marginTop: 18, background: "#16a34a", color: "#fff", textDecoration: "none", padding: "13px 18px", borderRadius: 14, fontWeight: 900 }}>Continue to login</a>
      </section>
    </main>
  );
}
'''

cancel = '''export default function BillingCancelPage() {
  return (
    <main style={{ minHeight: "100vh", padding: 32, fontFamily: "Inter, system-ui, Arial", background: "#f8fafc", color: "#101828" }}>
      <section style={{ maxWidth: 760, margin: "0 auto", background: "#fff", border: "1px solid #fee2e2", borderRadius: 24, padding: 32, boxShadow: "0 18px 50px rgba(15,23,42,.08)" }}>
        <div style={{ color: "#dc2626", fontWeight: 900, letterSpacing: ".08em", fontSize: 12 }}>CHECKOUT CANCELLED</div>
        <h1 style={{ fontSize: 34, margin: "10px 0 8px" }}>Checkout was not completed</h1>
        <p style={{ color: "#667085", lineHeight: 1.6 }}>No subscription was activated. You can return to signup and choose your plan again.</p>
        <a href="/signup" style={{ display: "inline-block", marginTop: 18, background: "#635BFF", color: "#fff", textDecoration: "none", padding: "13px 18px", borderRadius: 14, fontWeight: 900 }}>Back to signup</a>
      </section>
    </main>
  );
}
'''

(base / "page.tsx").write_text(page, encoding="utf-8")
(base / "success").mkdir(exist_ok=True)
(base / "success" / "page.tsx").write_text(success, encoding="utf-8")
(base / "cancel").mkdir(exist_ok=True)
(base / "cancel" / "page.tsx").write_text(cancel, encoding="utf-8")
(base / "cancelled").mkdir(exist_ok=True)
(base / "cancelled" / "page.tsx").write_text(cancel, encoding="utf-8")

print("BILLING_RETURN_PAGES_ADDED")