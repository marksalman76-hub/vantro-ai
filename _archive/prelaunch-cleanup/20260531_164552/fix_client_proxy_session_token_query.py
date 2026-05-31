from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = BACKUPS / f"client_proxy_session_token_query_{stamp}"
backup_dir.mkdir(exist_ok=True)

files = [
    "frontend/src/app/api/client-me/route.ts",
    "frontend/src/app/api/client-business-profile/route.ts",
]

for file_path in files:
    path = ROOT / file_path
    text = path.read_text(encoding="utf-8")
    (backup_dir / path.name).write_text(text, encoding="utf-8")

    if "function getSessionToken" not in text:
        text = text.replace(
            "function getBearer(req: NextRequest): string {",
            """function getSessionToken(req: NextRequest): string {
  const auth = req.headers.get("authorization") || "";
  if (auth.toLowerCase().startsWith("bearer ")) return auth.slice(7).trim();

  return (
    req.cookies.get("client_token")?.value ||
    req.cookies.get("token")?.value ||
    req.cookies.get("auth_token")?.value ||
    ""
  );
}

function getBearer(req: NextRequest): string {"""
        )

    text = text.replace(
        "const res = await fetch(`${BACKEND_URL}${path}`, init);",
        """const sessionToken = getSessionToken(req);
  let backendPath = path;

  if (sessionToken && (path === "/client/me" || path === "/client/business-profile")) {
    const joiner = backendPath.includes("?") ? "&" : "?";
    backendPath = `${backendPath}${joiner}session_token=${encodeURIComponent(sessionToken)}`;
  }

  const res = await fetch(`${BACKEND_URL}${backendPath}`, init);"""
    )

    path.write_text(text, encoding="utf-8")

print("CLIENT_PROXY_SESSION_TOKEN_QUERY_FIXED")
print("Backup:", backup_dir)