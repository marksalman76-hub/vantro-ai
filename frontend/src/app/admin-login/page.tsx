export default async function AdminLoginPage({
  searchParams,
}: {
  searchParams?: Promise<{ next?: string }>;
}) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const nextPath = resolvedSearchParams.next || "/admin";

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: 24,
        background: "#020617",
        color: "white",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      <form
        method="POST"
        action="/api/login"
        style={{
          width: "100%",
          maxWidth: 460,
          padding: 34,
          borderRadius: 24,
          background: "#111827",
          border: "1px solid rgba(245,158,11,.28)",
          boxShadow: "0 28px 90px rgba(0,0,0,.32)",
        }}
      >
        <p style={{ color: "#f59e0b", fontWeight: 800, letterSpacing: 1 }}>
          OWNER / ADMIN ACCESS
        </p>

        <h1 style={{ marginTop: 10, fontSize: 38, lineHeight: 1.1 }}>
          Admin control centre
        </h1>

        <input type="hidden" name="next" value={nextPath} />

        <label style={{ display: "block", marginTop: 20, marginBottom: 8 }}>
          Owner access code
        </label>
        <input
          name="access"
          type="password"
          placeholder="Owner access code"
          required
          style={{
            width: "100%",
            padding: 14,
            borderRadius: 10,
            border: "1px solid rgba(148,163,184,.35)",
          }}
        />

        <button
          type="submit"
          style={{
            width: "100%",
            marginTop: 20,
            padding: 14,
            borderRadius: 10,
            border: 0,
            background: "#f59e0b",
            color: "#111827",
            fontWeight: 800,
            cursor: "pointer",
          }}
        >
          Login as Owner/Admin
        </button>
      </form>
    </main>
  );
}
