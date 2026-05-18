import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

checks = []
failed = []

def run(name, cmd, cwd=ROOT):
    result = subprocess.run(cmd, cwd=str(cwd), shell=True, capture_output=True, text=True, timeout=180)
    ok = result.returncode == 0
    checks.append((name, ok))
    print(f"{name}: {'PASS' if ok else 'FAIL'}")
    if not ok:
        failed.append({
            "check": name,
            "stdout": result.stdout[-1000:],
            "stderr": result.stderr[-1000:],
        })

print("FINAL_LAUNCH_LOCK_START")

run("phase_e_regression", "python test_phase_e_launch_regression_readiness.py")
run("all_25_agents_execution", "python test_phase_a_all_25_agents_execution.py")
run("backend_main_compile", "python -m py_compile backend\\app\\main.py")
run("frontend_build", "npm run build", cwd=ROOT / "frontend")
run("git_status", "git status --short")

print("")
print("FINAL_LAUNCH_LOCK_RESULTS")
print("TOTAL_CHECKS", len(checks))
print("FAILED_COUNT", len(failed))

if failed:
    print("FAILED_DETAILS")
    for item in failed:
        print(item)
else:
    print("FINAL_LAUNCH_LOCK_READY")
    print("Timestamp:", datetime.now().isoformat())