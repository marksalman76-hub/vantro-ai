from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
RUNTIME = ROOT / "backend" / "app" / "core" / "postgres_account_runtime.py"

text = RUNTIME.read_text(encoding="utf-8")

old_block = """            return {
                "success": True,
                "account": {
                    "tenant_id": row[0],
                    "email": row[1],
                    "company_name": row[2],
                    "package": row[3],
                    "active_agents": json.loads(row[4] or "[]"),
                    "status": row[5],
                },
            }"""

new_block = """            monthly_credits = int(row[6] or 0)
            credits_used = int(row[7] or 0)
            credits_remaining = max(monthly_credits - credits_used, 0)

            return {
                "success": True,
                "account": {
                    "tenant_id": row[0],
                    "email": row[1],
                    "company_name": row[2],
                    "package": row[3],
                    "active_agents": json.loads(row[4] or "[]"),
                    "status": row[5],
                    "monthly_credits": monthly_credits,
                    "credits_used": credits_used,
                    "credits_remaining": credits_remaining,
                },
            }"""

if old_block not in text:
    raise SystemExit(
        "Expected session account serialization block not found. Stop and inspect postgres_account_runtime.py"
    )

text = text.replace(old_block, new_block)

RUNTIME.write_text(text, encoding="utf-8")

print("STEP_184_FIX_SESSION_CREDIT_SERIALIZATION_INSTALLED")
print("updated", RUNTIME)
print("STEP_184_OK")