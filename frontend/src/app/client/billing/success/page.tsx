export default function BillingSuccessPage() {
  return (
    <main style={{ minHeight: "100vh", padding: 32, fontFamily: "Inter, system-ui, Arial", background: "#e2e8f0", color: "#f8fafc" }}>
      <section style={{ maxWidth: 760, margin: "0 auto", background: "rgba(15,23,42,.92)", border: "1px solid #dcfce7", borderRadius: 24, padding: 32, boxShadow: "0 18px 50px rgba(15,23,42,.08)" }}>
        <div style={{ color: "#8b5cf6", fontWeight: 900, letterSpacing: ".08em", fontSize: 12 }}>PAYMENT SUCCESSFUL</div>
        <h1 style={{ fontSize: 34, margin: "10px 0 8px" }}>Your subscription is being activated</h1>
        <p style={{ color: "#667085", lineHeight: 1.6 }}>Payment was successful. Your account, selected agents, and activation access will be prepared according to your plan.</p>
        <a href="/login" style={{ display: "inline-block", marginTop: 18, background: "#8b5cf6", color: "#fff", textDecoration: "none", padding: "13px 18px", borderRadius: 14, fontWeight: 900 }}>Continue to login</a>
      </section>
    </main>
  );
}
