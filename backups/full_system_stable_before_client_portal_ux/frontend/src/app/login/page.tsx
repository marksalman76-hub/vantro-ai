export default async function LoginPage({
  searchParams,
}: {
  searchParams?: Promise<{ next?: string }>;
}) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const nextPath = resolvedSearchParams.next || "/client";

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
        action="/api/client-login"
        style={{
          width: "100%",
          maxWidth: 460,
          padding: 34,
          borderRadius: 24,
          background: "#0f172a",
          border: "1px solid rgba(148,163,184,.25)",
          boxShadow: "0 28px 90px rgba(0,0,0,.32)",
        }}
      >
        <p style={{ color: "#38bdf8", fontWeight: 800, letterSpacing: 1 }}>
          CLIENT LOGIN
        </p>

        <h1 style={{ marginTop: 10, fontSize: 38, lineHeight: 1.1 }}>
          Access your workspace
        </h1>

        <input type="hidden" name="next" value={nextPath} />

        <label style={{ display: "block", marginTop: 20, marginBottom: 8 }}>
          Email
        </label>
        <input
          name="email"
          type="email"
          placeholder="client@example.com"
          required
          style={{
            width: "100%",
            padding: 14,
            borderRadius: 10,
            border: "1px solid rgba(148,163,184,.35)",
          }}
        />

        <label style={{ display: "block", marginTop: 16, marginBottom: 8 }}>
          Password
        </label>
        <input
          name="password"
          type="password"
          placeholder="Password"
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
            background: "#2563eb",
            color: "white",
            fontWeight: 800,
            cursor: "pointer",
          }}
        >
          Login as Client
        </button>
      </form>
    </main>
  );
}
