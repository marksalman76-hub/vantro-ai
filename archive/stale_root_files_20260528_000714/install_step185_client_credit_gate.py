from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
RUNTIME = ROOT / "backend" / "app" / "core" / "postgres_account_runtime.py"

text = RUNTIME.read_text(encoding="utf-8")

credit_gate_code = r'''

def client_credit_gate(payload: dict):
    actor_role = str(payload.get("actor_role") or "client").strip().lower()

    if actor_role in {"owner", "admin", "system"}:
        return {
            "success": True,
            "credit_gate_passed": True,
            "bypass_reason": "owner_admin_system_execution_unrestricted_by_client_credits",
            "credits_required": False,
        }

    tenant_id = str(payload.get("tenant_id") or "").strip()
    requested_credits = int(payload.get("requested_credits") or 1)

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT monthly_credits, credits_used
            FROM client_accounts
            WHERE tenant_id = %s AND status = 'active'
            """, (tenant_id,))

            row = cur.fetchone()

    if not row:
        return {
            "success": False,
            "credit_gate_passed": False,
            "error": "active_client_account_not_found",
        }

    monthly_credits = int(row[0] or 0)
    credits_used = int(row[1] or 0)
    credits_remaining = max(monthly_credits - credits_used, 0)

    if credits_remaining <= 0:
        return {
            "success": False,
            "credit_gate_passed": False,
            "error": "client_monthly_credits_exhausted",
            "execution_status": "blocked_until_top_up_or_next_billing_cycle",
            "monthly_credits": monthly_credits,
            "credits_used": credits_used,
            "credits_remaining": credits_remaining,
            "top_up_required": True,
        }

    if requested_credits > credits_remaining:
        return {
            "success": False,
            "credit_gate_passed": False,
            "error": "insufficient_client_credits",
            "execution_status": "blocked_until_top_up_or_next_billing_cycle",
            "monthly_credits": monthly_credits,
            "credits_used": credits_used,
            "credits_remaining": credits_remaining,
            "requested_credits": requested_credits,
            "top_up_required": True,
        }

    return {
        "success": True,
        "credit_gate_passed": True,
        "credits_required": True,
        "monthly_credits": monthly_credits,
        "credits_used": credits_used,
        "credits_remaining": credits_remaining,
        "requested_credits": requested_credits,
    }
'''

if "def client_credit_gate" not in text:
    text = text.rstrip() + "\n" + credit_gate_code + "\n"

RUNTIME.write_text(text, encoding="utf-8")

print("STEP_185_CLIENT_CREDIT_GATE_INSTALLED")
print("owner_admin_bypass", True)
print("client_credit_exhaustion_blocks_execution", True)
print("STEP_185_OK")
