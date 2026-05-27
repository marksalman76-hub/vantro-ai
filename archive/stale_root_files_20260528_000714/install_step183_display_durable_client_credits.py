from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"

text = CLIENT_PAGE.read_text(encoding="utf-8")

text = text.replace(
    """  status?: string;
  created_at?: string;
  activated_at?: string;
};""",
    """  status?: string;
  created_at?: string;
  activated_at?: string;
  monthly_credits?: number;
  credits_used?: number;
  credits_remaining?: number;
};""",
)

old_credit_block = """  const monthlyCreditAllocation = 0;
  const creditsUsed = 0;
  const creditsRemaining = monthlyCreditAllocation - creditsUsed;
  const usagePercentage =
    monthlyCreditAllocation > 0
      ? Math.round((creditsUsed / monthlyCreditAllocation) * 100)
      : 0;"""

new_credit_block = """  const monthlyCreditAllocation = account?.monthly_credits ?? 0;
  const creditsUsed = account?.credits_used ?? 0;
  const creditsRemaining =
    account?.credits_remaining ?? Math.max(monthlyCreditAllocation - creditsUsed, 0);
  const usagePercentage =
    monthlyCreditAllocation > 0
      ? Math.round((creditsUsed / monthlyCreditAllocation) * 100)
      : 0;"""

if old_credit_block not in text:
    raise SystemExit("Expected static credit block not found. Stop and send current client page.")

text = text.replace(old_credit_block, new_credit_block)

CLIENT_PAGE.write_text(text, encoding="utf-8")

print("STEP_183_DISPLAY_DURABLE_CLIENT_CREDITS_INSTALLED")
print("updated", CLIENT_PAGE)
print("STEP_183_OK")