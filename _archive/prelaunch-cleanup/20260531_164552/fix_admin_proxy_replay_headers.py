from pathlib import Path

p = Path("frontend/src/app/api/admin-deployment-control/route.ts")
s = p.read_text(encoding="utf-8")

old = '''    if (ADMIN_TOKEN) {
      headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
      headers["x-admin-token"] = ADMIN_TOKEN;
    }'''

new = '''    const requestId =
      request.headers.get("x-request-id") ||
      `admin-${Date.now()}-${Math.random().toString(36).slice(2)}`;

    const idempotencyKey =
      request.headers.get("x-idempotency-key") || requestId;

    headers["x-request-id"] = requestId;
    headers["x-idempotency-key"] = idempotencyKey;
    headers["x-csrf-token"] = requestId;

    if (ADMIN_TOKEN) {
      headers.Authorization = `Bearer ${ADMIN_TOKEN}`;
      headers["x-admin-token"] = ADMIN_TOKEN;
    }'''

if old not in s:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")

print("ADMIN_PROXY_REPLAY_HEADERS_FIXED")