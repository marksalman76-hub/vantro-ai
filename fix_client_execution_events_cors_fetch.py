from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''        `${BACKEND_API_BASE}/client/execution-events?tenant_id=${encodeURIComponent(eventTenantId)}&project_id=live_readiness_matrix&limit=20`,'''

new = '''        `/api/client-latest-deliverable`,'''

if old not in text:
    raise SystemExit("Direct execution-events fetch anchor not found")

text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")
print("CLIENT_EXECUTION_EVENTS_CORS_FETCH_FIXED")