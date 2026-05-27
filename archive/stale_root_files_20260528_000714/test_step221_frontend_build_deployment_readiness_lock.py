from pathlib import Path
import json
import subprocess
import sys

ROOT = Path.cwd()

possible_frontends = [
    ROOT / "apps" / "web",
    ROOT / "frontend",
    ROOT / "web",
]

frontend_path = None

for path in possible_frontends:
    if (path / "package.json").exists():
        frontend_path = path
        break

checks = {}

checks["frontend_detected"] = frontend_path is not None

if frontend_path is None:
    print("STEP_221_FRONTEND_BUILD_DEPLOYMENT_READINESS_LOCK_RESULTS")
    print("frontend_detected", False)
    print("frontend_optional_for_current_repo", True)
    print("STEP_221_FRONTEND_BUILD_DEPLOYMENT_READINESS_LOCK_OK")
    raise SystemExit(0)

package_json = frontend_path / "package.json"

checks["package_json_exists"] = package_json.exists()

package = {}
if package_json.exists():
    package = json.loads(package_json.read_text(encoding="utf-8"))

scripts = package.get("scripts", {})
dependencies = {
    **package.get("dependencies", {}),
    **package.get("devDependencies", {}),
}

checks["build_script_exists"] = "build" in scripts
checks["next_dependency_exists"] = "next" in dependencies or "vite" in dependencies
checks["react_dependency_exists"] = "react" in dependencies

print("STEP_221_FRONTEND_BUILD_DEPLOYMENT_READINESS_LOCK_RESULTS")
print("frontend_path", str(frontend_path))

for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED_STATIC_CHECKS", failed)
    raise SystemExit(1)

print("RUNNING_FRONTEND_BUILD")

result = subprocess.run(
    ["cmd", "/c", "npm run build"],
    cwd=str(frontend_path),
    text=True,
)

print("frontend_build_exit_code", result.returncode)

if result.returncode != 0:
    print("FAILED_FRONTEND_BUILD")
    raise SystemExit(result.returncode)

print("STEP_221_FRONTEND_BUILD_DEPLOYMENT_READINESS_LOCK_OK")