from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
RUNTIME = ROOT / "backend" / "app" / "core" / "postgres_account_runtime.py"
MAIN = ROOT / "backend" / "app" / "main.py"

runtime_text = RUNTIME.read_text(encoding="utf-8")

runtime_text = runtime_text.replace(
    "\ninitialise_tables()\n",
    r'''

POSTGRES_STARTUP_STATUS = {
    "available": False,
    "initialised": False,
    "error": None,
}


def safe_initialise_tables():
    try:
        initialise_tables()
        POSTGRES_STARTUP_STATUS["available"] = True
        POSTGRES_STARTUP_STATUS["initialised"] = True
        POSTGRES_STARTUP_STATUS["error"] = None
    except Exception as exc:
        POSTGRES_STARTUP_STATUS["available"] = False
        POSTGRES_STARTUP_STATUS["initialised"] = False
        POSTGRES_STARTUP_STATUS["error"] = str(exc)


def database_readiness():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                row = cur.fetchone()

        return {
            "success": True,
            "database_available": True,
            "startup_status": POSTGRES_STARTUP_STATUS,
            "test_result": row[0] if row else None,
        }
    except Exception as exc:
        return {
            "success": False,
            "database_available": False,
            "startup_status": POSTGRES_STARTUP_STATUS,
            "error": str(exc),
        }


safe_initialise_tables()
''',
)

RUNTIME.write_text(runtime_text, encoding="utf-8")

main_text = MAIN.read_text(encoding="utf-8")

if "database_readiness as pg_database_readiness" not in main_text:
    main_text = main_text.replace(
        "    assign_client_credits as pg_assign_client_credits,\n)",
        "    assign_client_credits as pg_assign_client_credits,\n"
        "    database_readiness as pg_database_readiness,\n)",
    )

route_code = r'''

@app.get("/admin/database-readiness")
async def durable_database_readiness():
    return pg_database_readiness()
'''

if "/admin/database-readiness" not in main_text:
    main_text = main_text.rstrip() + "\n" + route_code + "\n"

MAIN.write_text(main_text, encoding="utf-8")

print("STEP_177_SAFE_DATABASE_STARTUP_INSTALLED")
print("database failures will not crash app startup")
print("added /admin/database-readiness")
print("STEP_177_OK")