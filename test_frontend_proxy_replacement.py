from pathlib import Path

proxy = Path("frontend/proxy.ts")
middleware_root = Path("frontend/middleware.ts")
middleware_src = Path("frontend/src/middleware.ts")

text = proxy.read_text(encoding="utf-8") if proxy.exists() else ""

print("FRONTEND_PROXY_REPLACEMENT_RESULTS")
print("proxy_exists", proxy.exists())
print("root_middleware_removed", not middleware_root.exists())
print("src_middleware_removed", not middleware_src.exists())
print("exports_proxy", "export function proxy" in text)
print("exports_config", "export const config" in text)
print("admin_matcher", '"/admin/:path*"' in text)
print("client_matcher", '"/client/:path*"' in text)

assert proxy.exists()
assert not middleware_root.exists()
assert not middleware_src.exists()
assert "export function proxy" in text
assert "export const config" in text
assert '"/admin/:path*"' in text
assert '"/client/:path*"' in text

print("FRONTEND_PROXY_REPLACEMENT_OK")
