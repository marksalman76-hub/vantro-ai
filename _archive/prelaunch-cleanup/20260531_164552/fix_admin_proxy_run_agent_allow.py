from pathlib import Path

path = Path("frontend/src/app/api/admin-deployment-control/route.ts")

s = path.read_text(encoding="utf-8")

old = '''function safePath(path: string) {
  if (!path || typeof path !== "string") return "";
  if (!path.startsWith("/admin/deployment-control/")) return "";
  return path;
}'''

new = '''function safePath(path: string) {
  if (!path || typeof path !== "string") return "";

  if (path === "/run-agent") {
    return path;
  }

  if (path.startsWith("/admin/deployment-control/")) {
    return path;
  }

  return "";
}'''

if old not in s:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

s = s.replace(old, new, 1)

path.write_text(s, encoding="utf-8")

print("ADMIN_PROXY_RUN_AGENT_ALLOW_FIXED")