export const dynamic = "force-dynamic";
export const revalidate = 0;

import AdminLoginSupportClient from "./support-client";

export default async function AdminLoginPage({
  searchParams,
}: {
  searchParams?: Promise<{ next?: string }>;
}) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const nextPath = resolvedSearchParams.next || "/admin";

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24, background: "radial-gradient(circle at top right, rgba(99,91,255,.24) 0, transparent 34%), radial-gradient(circle at bottom left, rgba(20,184,166,.18) 0, transparent 30%), linear-gradient(135deg, #050816 0%, #0b1020 55%, #050816 100%)", color: "#f8fafc", fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" }}>
      <form method="POST" action="/api/login" style={{ width: "100%", maxWidth: 520, padding: 38, borderRadius: 28, background: "linear-gradient(180deg, rgba(15,23,42,.92), rgba(7,16,34,.96))", border: "1px solid rgba(148,163,184,.22)", boxShadow: "0 30px 90px rgba(0,0,0,.38)" }}>
        <p style={{ color: "#a78bfa", fontWeight: 900, letterSpacing: 1.3, fontSize: 12, textAlign: "center" }}>OWNER / ADMIN ACCESS</p>
        <h1 style={{ margin: "12px 0 10px", fontSize: 34, lineHeight: 1.05, letterSpacing: "-.04em", textAlign: "center" }}>Admin control centre</h1>
        <p style={{ margin: "0 0 24px", color: "#cbd5e1", lineHeight: 1.6, textAlign: "center" }}>Restricted access for platform owners and administrators.</p>
        <input type="hidden" name="next" value={nextPath} />
        <label style={{ display: "block", marginTop: 20, marginBottom: 8, color: "#e2e8f0", fontWeight: 800 }}>Owner access code</label>
        <input name="access" type="password" placeholder="Enter owner access code" required style={{ width: "100%", padding: 14, borderRadius: 14, border: "1px solid rgba(148,163,184,.26)", background: "rgba(3,10,24,.72)", color: "#f8fafc", fontSize: 14, boxSizing: "border-box", outline: "none" }} />
        <button type="submit" style={{ width: "100%", marginTop: 22, padding: 15, borderRadius: 14, border: 0, background: "linear-gradient(135deg,#635BFF,#8b5cf6)", color: "white", fontWeight: 900, cursor: "pointer", boxShadow: "0 16px 42px rgba(99,91,255,.30)" }}>Login as Owner/Admin</button>
        <div style={{ marginTop: 24, paddingTop: 20, borderTop: "1px solid rgba(148,163,184,.16)", color: "#94a3b8", textAlign: "center", fontSize: 13 }}>Secure access · All actions are logged</div>
      </form>

      <AdminLoginSupportClient />
    </main>
  );
}
