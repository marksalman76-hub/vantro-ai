from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step247_customer_execution_smoke_lock.py"
FIX = ROOT / "fix_step247b_assign_customer_smoke_credits.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"test_step247_before_step247b_{timestamp}.py"
backup.write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")

text = TEST.read_text(encoding="utf-8")

insert = r'''
def assign_credits(tenant_id: str):
    payload = {
        "tenant_id": tenant_id,
        "monthly_credits": 25,
        "credits_used": 0,
        "reason": "Step 247 customer execution smoke test credit allocation.",
    }

    req = urllib.request.Request(
        BASE + "/admin/assign-client-credits",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = {"raw": body}
        return exc.code, data

'''

if "def assign_credits" not in text:
    marker = "tenant_id = \"client_step245_smoke\"\n"
    if marker not in text:
        raise RuntimeError("tenant_id marker not found")

    text = text.replace(marker, insert + "\n" + marker + "\ncredit_status, credit_result = assign_credits(tenant_id)\n")

text = text.replace(
    '''print("http_status", status)''',
    '''print("credit_status", credit_status)
print("credit_assigned", credit_result.get("success") if isinstance(credit_result, dict) else None)
print("http_status", status)'''
)

text = text.replace(
    '''"run_agent_status_controlled": status in {200, 402, 403, 422},''',
    '''"credit_assignment_success": credit_status in {200, 201} and credit_result.get("success") is True,
    "run_agent_status_controlled": status in {200, 402, 403, 422},'''
)

TEST.write_text(text, encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_247B_ASSIGN_CUSTOMER_SMOKE_CREDITS_PATCH_OK")
print(f"Backup: {backup}")
print(f"Updated: {TEST}")