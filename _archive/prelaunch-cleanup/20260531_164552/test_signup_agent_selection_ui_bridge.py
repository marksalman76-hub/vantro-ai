from pathlib import Path

ROOT = Path.cwd()

component = ROOT / "frontend/src/components/SignupAgentSelectionBridge.tsx"
signup = ROOT / "frontend/src/app/signup/page.tsx"

assert component.exists(), "SignupAgentSelectionBridge component missing"
assert signup.exists(), "signup page missing"

component_text = component.read_text(encoding="utf-8")
signup_text = signup.read_text(encoding="utf-8")

assert "/api/signup-agent-selection/options/" in component_text
assert "/api/signup-agent-selection/validate" in component_text
assert "Choose your active agents" in component_text
assert "Head Agent reserved for Enterprise" in component_text
assert "SignupAgentSelectionBridge" in signup_text
assert "@/components/SignupAgentSelectionBridge" in signup_text

print("SIGNUP_AGENT_SELECTION_UI_BRIDGE_TESTS_PASSED")
print("component_present", component.exists())
print("signup_wired", "SignupAgentSelectionBridge" in signup_text)
