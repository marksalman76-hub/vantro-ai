export default function LoginPage({
  searchParams,
}: {
  searchParams?: { next?: string };
}) {
  const nextPath = searchParams?.next || "/admin";

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#020617", color: "white", fontFamily: "Arial, sans-serif" }}>
      <form method="POST" action="/api/login" style={{ width: "100%", maxWidth: 420, padding: 32, borderRadius: 20, background: "#0f172a" }}>
        <h1>Portal Login</h1>
        <input type="hidden" name="next" value={nextPath} />
        <input name="access" type="password" placeholder="Access code" required style={{ width: "100%", padding: 14, marginTop: 20, borderRadius: 10 }} />
        <button type="submit" style={{ width: "100%", marginTop: 16, padding: 14, borderRadius: 10, fontWeight: 700 }}>
          Enter Portal
        </button>
      </form>
    </main>
  );
}