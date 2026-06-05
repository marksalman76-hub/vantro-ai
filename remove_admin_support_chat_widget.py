from pathlib import Path

ROOT = Path.cwd()
admin_login = ROOT / "frontend/src/app/admin-login/page.tsx"

text = admin_login.read_text(encoding="utf-8")
original = text

text = text.replace('import AdminLoginSupportClient from "./support-client";\n', "")
text = text.replace("      <AdminLoginSupportClient />\n", "")

admin_login.write_text(text, encoding="utf-8")

if text != original:
    print("REMOVED_ADMIN_LOGIN_SUPPORT_CHAT_WIDGET")
else:
    print("NO_ADMIN_LOGIN_SUPPORT_CHAT_WIDGET_CHANGE")