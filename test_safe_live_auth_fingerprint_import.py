from backend.app.main import app

routes = [getattr(route, "path", "") for route in app.routes]

assert "/debug/live-auth-fingerprint" in routes

print("SAFE_LIVE_AUTH_FINGERPRINT_IMPORT_OK")
