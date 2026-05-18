from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "activate" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"activate_page_before_current_fetch_fix_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

if 'import { headers } from "next/headers";' not in text:
    text = 'import { headers } from "next/headers";\n' + text

old = '''async function getInviteStatus(token: string) {
  try {
    const response = await fetch(
  `/api/activation-invite-status?token=${encodeURIComponent(token)}`,
  { cache: "no-store" }
);'''

new = '''async function getInviteStatus(token: string) {
  try {
    const headerStore = await headers();
    const host = headerStore.get("host") || "ecommerce-ai-agent-platform.vercel.app";
    const proto = headerStore.get("x-forwarded-proto") || "https";
    const origin = `${proto}://${host}`;

    const response = await fetch(
      `${origin}/api/activation-invite-status?token=${encodeURIComponent(token)}`,
      { cache: "no-store" }
    );'''

if old not in text:
    raise SystemExit("TARGET_FETCH_BLOCK_NOT_FOUND_AGAIN")

text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("ACTIVATION_PAGE_CURRENT_FETCH_FIXED")
print(f"Backup: {backup}")