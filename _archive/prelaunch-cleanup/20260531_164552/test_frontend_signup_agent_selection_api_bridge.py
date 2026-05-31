
from pathlib import Path

ROOT = Path.cwd()

expected_files = [
    ROOT / "frontend/src/app/api/signup-agent-selection/options/[plan]/route.ts",
    ROOT / "frontend/src/app/api/signup-agent-selection/validate/route.ts",
    ROOT / "frontend/src/app/api/signup-agent-selection/activation-packet/route.ts",
]

for path in expected_files:
    assert path.exists(), f"Missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "signup-agent-selection" in text
    assert "NextResponse.json" in text
    assert "cache: \"no-store\"" in text

options = expected_files[0].read_text(encoding="utf-8")
assert "/signup-agent-selection/options/" in options

validate = expected_files[1].read_text(encoding="utf-8")
assert "/signup-agent-selection/validate" in validate

activation = expected_files[2].read_text(encoding="utf-8")
assert "/signup-agent-selection/activation-packet" in activation

print("FRONTEND_SIGNUP_AGENT_SELECTION_API_BRIDGE_TESTS_PASSED")
print("routes", len(expected_files))
