from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

if "client_credit_gate as pg_client_credit_gate" not in text:
    text = text.replace(
        "    lookup_client_account as pg_lookup_client_account,\n)",
        "    lookup_client_account as pg_lookup_client_account,\n"
        "    client_credit_gate as pg_client_credit_gate,\n)",
    )

route_code = r'''

@app.post("/admin/client-credit-gate/test")
async def durable_client_credit_gate_test(payload: dict):
    return pg_client_credit_gate(payload)
'''

if "/admin/client-credit-gate/test" not in text:
    text = text.rstrip() + "\n" + route_code + "\n"

MAIN.write_text(text, encoding="utf-8")

print("STEP_186_CREDIT_GATE_TEST_ROUTE_INSTALLED")
print("STEP_186_OK")