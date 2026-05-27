from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
RUNTIME = ROOT / "backend" / "app" / "core" / "postgres_account_runtime.py"
MAIN = ROOT / "backend" / "app" / "main.py"

runtime_text = RUNTIME.read_text(encoding="utf-8")

credit_code = r'''

def assign_client_credits(payload: dict):
    tenant_id = str(payload.get("tenant_id") or "").strip()
    monthly_credits = int(payload.get("monthly_credits") or 0)
    top_up_credits = int(payload.get("top_up_credits") or 0)

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE client_accounts
            SET monthly_credits = %s,
                credits_used = GREATEST(credits_used - %s, 0)
            WHERE tenant_id = %s
            RETURNING tenant_id, email, company_name, package_name, active_agents, status, monthly_credits, credits_used
            """, (
                monthly_credits,
                top_up_credits,
                tenant_id,
            ))

            row = cur.fetchone()

        conn.commit()

    if not row:
        return {"success": False, "error": "client_account_not_found"}

    return {
        "success": True,
        "account": {
            "tenant_id": row[0],
            "email": row[1],
            "company_name": row[2],
            "package": row[3],
            "active_agents": json.loads(row[4] or "[]"),
            "status": row[5],
            "monthly_credits": row[6],
            "credits_used": row[7],
            "credits_remaining": max(int(row[6]) - int(row[7]), 0),
        },
    }
'''

if "def assign_client_credits" not in runtime_text:
    runtime_text = runtime_text.rstrip() + "\n" + credit_code + "\n"

RUNTIME.write_text(runtime_text, encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

import_addition = "    assign_client_credits as pg_assign_client_credits,\n"

if "assign_client_credits as pg_assign_client_credits" not in main_text:
    main_text = main_text.replace(
        "    recent_security_events as pg_recent_security_events,\n)",
        "    recent_security_events as pg_recent_security_events,\n" + import_addition + ")",
    )

route_code = r'''

@app.post("/admin/client-credits/assign")
async def durable_assign_client_credits(payload: dict):
    return pg_assign_client_credits(payload)
'''

if "/admin/client-credits/assign" not in main_text:
    main_text = main_text.rstrip() + "\n" + route_code + "\n"

MAIN.write_text(main_text, encoding="utf-8")

print("STEP_176_ADMIN_CREDIT_ASSIGNMENT_INSTALLED")
print("updated", RUNTIME)
print("updated", MAIN)
print("STEP_176_OK")