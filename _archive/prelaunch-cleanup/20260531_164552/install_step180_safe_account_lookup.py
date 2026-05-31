from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
RUNTIME = ROOT / "backend" / "app" / "core" / "postgres_account_runtime.py"
MAIN = ROOT / "backend" / "app" / "main.py"

runtime_text = RUNTIME.read_text(encoding="utf-8")

lookup_code = r'''

def lookup_client_account(identifier: str):
    identifier = str(identifier or "").strip().lower()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT
                tenant_id,
                email,
                company_name,
                package_name,
                active_agents,
                status,
                monthly_credits,
                credits_used
            FROM client_accounts
            WHERE lower(tenant_id) = %s OR lower(email) = %s
            """, (identifier, identifier))

            row = cur.fetchone()

    if not row:
        return {"success": False, "error": "client_account_not_found", "identifier": identifier}

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

if "def lookup_client_account" not in runtime_text:
    runtime_text = runtime_text.rstrip() + "\n" + lookup_code + "\n"

RUNTIME.write_text(runtime_text, encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

if "lookup_client_account as pg_lookup_client_account" not in main_text:
    main_text = main_text.replace(
        "    database_readiness as pg_database_readiness,\n)",
        "    database_readiness as pg_database_readiness,\n"
        "    lookup_client_account as pg_lookup_client_account,\n)",
    )

route_code = r'''

@app.get("/admin/client-account/lookup")
async def durable_lookup_client_account(identifier: str):
    return pg_lookup_client_account(identifier)
'''

if "/admin/client-account/lookup" not in main_text:
    main_text = main_text.rstrip() + "\n" + route_code + "\n"

MAIN.write_text(main_text, encoding="utf-8")

print("STEP_180_SAFE_ACCOUNT_LOOKUP_INSTALLED")
print("STEP_180_OK")