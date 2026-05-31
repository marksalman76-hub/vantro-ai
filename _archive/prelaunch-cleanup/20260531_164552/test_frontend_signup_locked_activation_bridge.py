from pathlib import Path

ROOT = Path.cwd()

EXPECTED_FILES = [
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "status" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "draft" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "activate" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "change-request" / "route.ts",
]

for path in EXPECTED_FILES:
    assert path.exists(), f"Missing expected file: {path}"
    text = path.read_text(encoding="utf-8")
    assert "signup-locked-activation" in text, f"Missing route bridge marker in {path}"
    assert "ADMIN_PLATFORM_TOKEN" in text, f"Missing admin token fallback in {path}"
    assert "auth_required" in text, f"Missing auth guard response in {path}"
    assert "cache: \"no-store\"" in text, f"Missing no-store fetch policy in {path}"
    assert "credential" not in text.lower(), f"Unsafe credential wording found in {path}"

print("FRONTEND_SIGNUP_LOCKED_ACTIVATION_BRIDGE_TESTS_PASSED")
for path in EXPECTED_FILES:
    print("verified", path)
