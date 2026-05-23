from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FILE = ROOT / "backend" / "app" / "core" / "postgres_account_runtime.py"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"postgres_account_runtime_before_activation_conflict_fix_{stamp}.py"
shutil.copy2(FILE, backup)

text = FILE.read_text(encoding="utf-8")

old = '''    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client_accounts (
                tenant_id,
                email,
                company_name,
                package_name,
                active_agents,
                password_hash,
                status,
                created_at,
                activated_at,
                monthly_credits,
                credits_used
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                invite["tenant_id"],
                invite["email"],
                invite["company_name"],
                invite["package"],
                json.dumps(invite["active_agents"]),
                hash_password(password),
                "active",
                now,
                now,
                0,
                0
            ))

            cur.execute("""
            UPDATE client_activation_invites
            SET used = TRUE
            WHERE token = %s
            """, (token,))

        conn.commit()'''

new = '''    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Re-issued activation links for the same client/email must not crash
                # on tenant_id/email uniqueness. Replace the previous pending/active
                # account record for this same client identity, then activate fresh.
                cur.execute("""
                DELETE FROM client_accounts
                WHERE tenant_id = %s OR lower(email) = lower(%s)
                """, (
                    invite["tenant_id"],
                    invite["email"],
                ))

                cur.execute("""
                INSERT INTO client_accounts (
                    tenant_id,
                    email,
                    company_name,
                    package_name,
                    active_agents,
                    password_hash,
                    status,
                    created_at,
                    activated_at,
                    monthly_credits,
                    credits_used
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    invite["tenant_id"],
                    invite["email"],
                    invite["company_name"],
                    invite["package"],
                    json.dumps(invite["active_agents"]),
                    hash_password(password),
                    "active",
                    now,
                    now,
                    0,
                    0
                ))

                cur.execute("""
                UPDATE client_activation_invites
                SET used = TRUE
                WHERE token = %s
                """, (token,))

            conn.commit()
    except Exception as exc:
        return {
            "success": False,
            "error": "account_activation_database_error",
            "details": str(exc),
        }'''

if old not in text:
    raise SystemExit("TARGET_ACTIVATION_INSERT_BLOCK_NOT_FOUND")

text = text.replace(old, new)

FILE.write_text(text, encoding="utf-8")

print("POSTGRES_ACTIVATION_ACCOUNT_CONFLICT_FIXED")
print(f"Backup: {backup}")