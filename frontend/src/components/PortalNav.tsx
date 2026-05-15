export default function PortalNav() {
  return (
    <nav
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 36,
        paddingBottom: 18,
        borderBottom: "1px solid rgba(148,163,184,.2)",
      }}
    >
      <div>
        <strong style={{ fontSize: 20 }}>
          Ecommerce AI Agent Platform
        </strong>
      </div>

      <div
        style={{
          display: "flex",
          gap: 18,
          alignItems: "center",
        }}
      >
        <a
          href="/admin"
          style={{ color: "inherit", textDecoration: "none" }}
        >
          Admin
        </a>

        <a
          href="/client"
          style={{ color: "inherit", textDecoration: "none" }}
        >
          Client Portal
        </a>

        <a
          href="/api/logout"
          style={{
            textDecoration: "none",
            padding: "10px 14px",
            borderRadius: 10,
            background: "#dc2626",
            color: "white",
            fontWeight: 700,
          }}
        >
          Logout
        </a>
      </div>
    </nav>
  );
}