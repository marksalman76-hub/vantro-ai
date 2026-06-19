export const dynamic = "force-dynamic";
export const revalidate = 0;

export default function BillingCancelPage() {
  return (
    <main style={{ minHeight: "100vh", padding: 32, fontFamily: "Inter, system-ui, Arial", background: "#e2e8f0", color: "#f8fafc" }}>
      <section style={{ maxWidth: 760, margin: "0 auto", background: "rgba(15,23,42,.92)", border: "1px solid #fee2e2", borderRadius: 24, padding: 32, boxShadow: "0 18px 50px rgba(15,23,42,.08)" }}>
        <div style={{ color: "#dc2626", fontWeight: 900, letterSpacing: ".08em", fontSize: 12 }}>CHECKOUT CANCELLED</div>
        <h1 style={{ fontSize: 34, margin: "10px 0 8px" }}>Checkout was not completed</h1>
        <p style={{ color: "#667085", lineHeight: 1.6 }}>No subscription was activated. You can return to signup and choose your plan again.</p>
        <a href="/signup" style={{ display: "inline-block", marginTop: 18, background: "#635BFF", color: "#fff", textDecoration: "none", padding: "13px 18px", borderRadius: 14, fontWeight: 900 }}>Back to signup</a>
      </section>
    </main>
  );
}
