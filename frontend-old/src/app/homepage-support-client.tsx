"use client";

import React, { useEffect, useState } from "react";

type SupportChatProps = {
  cookieKey: string;
  sourceLabel: string;
};

function SupportChatWidget({ cookieKey, sourceLabel }: SupportChatProps) {
  const [cookieVisible, setCookieVisible] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("Hi, I’m your Support Agent. Ask me anything and I’ll help you here.");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    try {
      setCookieVisible(window.localStorage.getItem(cookieKey) !== "accepted");
    } catch {
      setCookieVisible(true);
    }
  }, [cookieKey]);

  function acceptCookies() {
    try { window.localStorage.setItem(cookieKey, "accepted"); } catch {}
    setCookieVisible(false);
  }

  function rejectCookies() {
    try { window.localStorage.setItem(cookieKey, "rejected"); } catch {}
    setCookieVisible(false);
  }

  async function sendMessage() {
    const text = message.trim();
    if (!text || busy) return;

    setBusy(true);
    setReply("Support Agent is thinking...");

    try {
      const response = await fetch("/api/support-agent-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: sourceLabel,
          message: text,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data?.success) {
        throw new Error(data?.error || "support_agent_failed");
      }

      const answer =
        data?.reply ||
        "Thanks — I have received your message. The Support Agent is active.";

      setReply(answer);
      setMessage("");
    } catch {
      setReply("I could not reach the live Support Agent right now. Please try again in a moment.");
    } finally {
      setBusy(false);
    }
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
        <div style={{ position: "fixed", right: 22, bottom: 22, width: "min(380px, calc(100vw - 44px))", borderRadius: 22, overflow: "hidden", background: "linear-gradient(180deg, rgba(15,23,42,.97), rgba(7,16,34,.99))", border: "1px solid rgba(148,163,184,.22)", boxShadow: "0 24px 80px rgba(0,0,0,.48)", color: "#f8fafc", zIndex: 56 }}>
          <div style={{ padding: 16, background: "linear-gradient(135deg,#635BFF,#8b5cf6)", display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
            <div><strong>Support Agent</strong><div style={{ fontSize: 12, opacity: .9 }}>{busy ? "Working..." : "Live"}</div></div>
            <button onClick={() => setChatOpen(false)} style={{ background: "transparent", border: 0, color: "#fff", fontSize: 22, cursor: "pointer" }}>×</button>
          </div>
          <div style={{ padding: 16 }}>
            <div style={{ background: "rgba(148,163,184,.12)", border: "1px solid rgba(148,163,184,.16)", borderRadius: 14, padding: 12, color: "#e2e8f0", fontSize: 13, lineHeight: 1.45, minHeight: 70 }}>
              {reply}
            </div>
            <textarea value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Type your message..." style={{ marginTop: 14, width: "100%", minHeight: 88, boxSizing: "border-box", resize: "vertical", borderRadius: 14, border: "1px solid rgba(148,163,184,.26)", background: "rgba(3,10,24,.72)", color: "#f8fafc", padding: 12, outline: "none", fontFamily: "inherit" }} />
            <button onClick={sendMessage} disabled={busy || !message.trim()} style={{ width: "100%", marginTop: 12, border: 0, borderRadius: 14, padding: 12, color: "#fff", fontWeight: 900, cursor: busy || !message.trim() ? "not-allowed" : "pointer", opacity: busy || !message.trim() ? .7 : 1, background: "linear-gradient(135deg,#635BFF,#8b5cf6)" }}>
              {busy ? "Sending..." : "Send to Support Agent"}
            </button>
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

export default function HomepageSupportClient() {
  return <SupportChatWidget cookieKey="nexus_home_cookie_consent" sourceLabel="Homepage" />;
}
