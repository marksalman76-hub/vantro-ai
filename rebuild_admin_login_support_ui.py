from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
page = root / "frontend" / "src" / "app" / "admin-login" / "page.tsx"
client = root / "frontend" / "src" / "app" / "admin-login" / "support-client.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"admin_login_before_cookie_chat_{stamp}.tsx"
backup.write_text(page.read_text(encoding="utf-8"), encoding="utf-8")

page.write_text('''import AdminLoginSupportClient from "./support-client";

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
''', encoding="utf-8")

client.write_text('''"use client";

import React, { useEffect, useState } from "react";

export default function AdminLoginSupportClient() {
  const [cookieVisible, setCookieVisible] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    try {
      setCookieVisible(window.localStorage.getItem("nexus_admin_cookie_consent") !== "accepted");
    } catch {
      setCookieVisible(true);
    }
  }, []);

  function acceptCookies() {
    try { window.localStorage.setItem("nexus_admin_cookie_consent", "accepted"); } catch {}
    setCookieVisible(false);
  }

  function rejectCookies() {
    try { window.localStorage.setItem("nexus_admin_cookie_consent", "rejected"); } catch {}
    setCookieVisible(false);
  }

  function sendMessage() {
    const text = message.trim();
    if (!text) return;
    const subject = encodeURIComponent("Admin login Support Agent request");
    const body = encodeURIComponent(`Support Agent message from admin login page:\\n\\n${text}`);
    window.location.href = `/support-request?subject=${subject}&message=${body}`;
  }

  return (
    <>
      {cookieVisible && (
        <div style={{ position: "fixed", left: 20, bottom: 20, width: "min(390px, calc(100vw - 40px))", padding: 20, borderRadius: 22, background: "linear-gradient(180deg, rgba(15,23,42,.96), rgba(7,16,34,.98))", border: "1px solid rgba(148,163,184,.22)", boxShadow: "0 24px 70px rgba(0,0,0,.45)", color: "#f8fafc", zIndex: 50 }}>
          <div style={{ fontSize: 26, marginBottom: 8 }}>🍪</div>
          <h3 style={{ margin: 0, fontSize: 18 }}>We value your privacy</h3>
          <p style={{ color: "#cbd5e1", lineHeight: 1.55, fontSize: 13 }}>We use cookies to improve your experience, support security, and understand site performance.</p>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <button onClick={rejectCookies} style={cookieButton}>Reject all</button>
            <a href="/cookies" style={{ ...cookieButton, textDecoration: "none", textAlign: "center" }}>Learn more</a>
            <button onClick={acceptCookies} style={{ ...cookieButton, background: "linear-gradient(135deg,#635BFF,#8b5cf6)", color: "#fff", border: 0 }}>Accept all</button>
          </div>
        </div>
      )}

      {!chatOpen && (
        <button onClick={() => setChatOpen(true)} aria-label="Open Support Agent chat" style={{ position: "fixed", right: 22, bottom: 22, width: 64, height: 64, borderRadius: 999, border: "1px solid rgba(167,139,250,.55)", background: "linear-gradient(135deg,#635BFF,#8b5cf6)", color: "#fff", fontSize: 27, boxShadow: "0 18px 48px rgba(99,91,255,.38)", cursor: "pointer", zIndex: 55 }}>
          🤖
        </button>
      )}

      {chatOpen && (
        <div style={{ position: "fixed", right: 22, bottom: 22, width: "min(360px, calc(100vw - 44px))", borderRadius: 22, overflow: "hidden", background: "linear-gradient(180deg, rgba(15,23,42,.97), rgba(7,16,34,.99))", border: "1px solid rgba(148,163,184,.22)", boxShadow: "0 24px 80px rgba(0,0,0,.48)", color: "#f8fafc", zIndex: 56 }}>
          <div style={{ padding: 16, background: "linear-gradient(135deg,#635BFF,#8b5cf6)", display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
            <div><strong>Support Agent</strong><div style={{ fontSize: 12, opacity: .9 }}>Online</div></div>
            <button onClick={() => setChatOpen(false)} style={{ background: "transparent", border: 0, color: "#fff", fontSize: 22, cursor: "pointer" }}>×</button>
          </div>
          <div style={{ padding: 16 }}>
            <div style={{ background: "rgba(148,163,184,.12)", border: "1px solid rgba(148,163,184,.16)", borderRadius: 14, padding: 12, color: "#e2e8f0", fontSize: 13, lineHeight: 1.45 }}>
              Hi, I’m your Support Agent. Send a message and I’ll route it to the support form.
            </div>
            <textarea value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Type your message..." style={{ marginTop: 14, width: "100%", minHeight: 88, boxSizing: "border-box", resize: "vertical", borderRadius: 14, border: "1px solid rgba(148,163,184,.26)", background: "rgba(3,10,24,.72)", color: "#f8fafc", padding: 12, outline: "none", fontFamily: "inherit" }} />
            <button onClick={sendMessage} style={{ width: "100%", marginTop: 12, border: 0, borderRadius: 14, padding: 12, color: "#fff", fontWeight: 900, cursor: "pointer", background: "linear-gradient(135deg,#635BFF,#8b5cf6)" }}>Send to support</button>
          </div>
        </div>
      )}
    </>
  );
}

const cookieButton: React.CSSProperties = {
  flex: 1,
  minWidth: 100,
  borderRadius: 12,
  border: "1px solid rgba(148,163,184,.24)",
  background: "rgba(15,23,42,.78)",
  color: "#e2e8f0",
  padding: "10px 12px",
  fontWeight: 850,
  cursor: "pointer",
};
''', encoding="utf-8")

print("ADMIN_LOGIN_COOKIE_AND_SUPPORT_AGENT_ADDED")
print("Backup:", backup)