from backend.app.main import app

routes = [getattr(route, "path", "") for route in app.routes]

assert "/system/live-auth-fingerprint" in routes

print("PUBLIC_SAFE_LIVE_AUTH_FINGERPRINT_IMPORT_OK")
