from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()

checks = []

def ok(name, detail=""):
    checks.append((name, True, detail))

def fail(name, detail=""):
    checks.append((name, False, detail))

def run(cmd):
    completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=True)
    return completed.returncode, completed.stdout, completed.stderr

required_files = [
    "AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md",
    "backend/app/runtime/durable_media_job_store.py",
    "test_durable_media_job_store.py",
    "frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx",
    "backend/app/runtime/direct_media_provider_execution_runtime.py",
]

for file in required_files:
    path = ROOT / file
    if path.exists():
        ok(f"file exists: {file}")
    else:
        fail(f"file missing: {file}")

# Verify migration matrix contains locked AWS target.
matrix = ROOT / "AWS_OPTION_A_MEDIA_MIGRATION_MATRIX.md"
if matrix.exists():
    text = matrix.read_text(encoding="utf-8", errors="ignore")
    for marker in [
        "ECS/Fargate",
        "SQS",
        "S3",
        "RDS PostgreSQL",
        "Human mode",
        "Use client-uploaded face/likeness",
        "duration",
        "not ecommerce-only",
        "Full-Stack AWS Option A Scope Addendum",
        "Admin portal",
        "Client portal",
        "Portal Authority Model",
        "Billing and credits",
        "Package enforcement",
        "Provider execution",
        "Security/session handling",
    ]:
        if marker.lower() in text.lower():
            ok(f"matrix marker: {marker}")
        else:
            fail(f"matrix marker missing: {marker}")

# Verify durable store keeps required fields.
store = ROOT / "backend/app/runtime/durable_media_job_store.py"
if store.exists():
    text = store.read_text(encoding="utf-8", errors="ignore")
    for marker in [
        "HumanMediaControls",
        "MediaCreativeControls",
        "MediaCreditEstimate",
        "DurableMediaJob",
        "LocalDurableMediaJobStore",
        "human_mode",
        "uploaded_likeness_asset_id",
        "explicit_likeness_consent",
        "estimate_credits",
    ]:
        if marker in text:
            ok(f"durable store marker: {marker}")
        else:
            fail(f"durable store marker missing: {marker}")

# Compile changed backend files.
for py_file in [
    "backend/app/runtime/durable_media_job_store.py",
    "backend/app/runtime/direct_media_provider_execution_runtime.py",
]:
    code, out, err = run(f'python -X utf8 -m py_compile "{py_file}"')
    if code == 0:
        ok(f"py_compile: {py_file}")
    else:
        fail(f"py_compile failed: {py_file}", err or out)

# Run durable store test.
code, out, err = run("python -X utf8 test_durable_media_job_store.py")
if code == 0 and "DURABLE_MEDIA_JOB_STORE_TEST_PASSED" in out:
    ok("durable media job store test")
else:
    fail("durable media job store test failed", err or out)

# Check current git diff only for awareness.
code, out, err = run("git status --short")
if code == 0:
    ok("git status readable", out.strip() or "clean except ignored/untracked local scripts")
else:
    fail("git status failed", err)

failed = [item for item in checks if not item[1]]

print("\nAWS_MIGRATION_SAFETY_CHECKPOINT")
print("=" * 40)

for name, passed, detail in checks:
    print(("PASS " if passed else "FAIL ") + name)
    if detail:
        print("  " + str(detail).replace("\n", "\n  ")[:1200])

print("=" * 40)

if failed:
    print(f"FAILED_CHECKS: {len(failed)}")
    sys.exit(1)

print("AWS_MIGRATION_SAFETY_CHECKPOINT_PASSED")