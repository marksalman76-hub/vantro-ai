export default function BillingPage() {
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
