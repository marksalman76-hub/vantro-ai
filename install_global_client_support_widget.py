from pathlib import Path

ROOT = Path.cwd()

client_wrapper = ROOT / "frontend/src/app/client-facing-support-widget.tsx"
client_wrapper.write_text(r'''"use client";

import { usePathname } from "next/navigation";
import HomepageSupportClient from "./homepage-support-client";

export default function ClientFacingSupportWidget() {
  const pathname = usePathname() || "";

  const blocked =
    pathname === "/admin" ||
    pathname === "/admin-login" ||
    pathname.startsWith("/admin/") ||
    pathname.startsWith("/api/");

  if (blocked) return null;

  return <HomepageSupportClient />;
}
''', encoding="utf-8")

layout = ROOT / "frontend/src/app/layout.tsx"
text = layout.read_text(encoding="utf-8")
original = text

if 'ClientFacingSupportWidget' not in text:
    text = text.replace(
        'import "./globals.css";',
        'import "./globals.css";\nimport ClientFacingSupportWidget from "./client-facing-support-widget";'
    )

    text = text.replace(
        "{children}",
        "{children}\n        <ClientFacingSupportWidget />",
        1
    )

layout.write_text(text, encoding="utf-8")

print("CREATED frontend/src/app/client-facing-support-widget.tsx")
print("PATCHED frontend/src/app/layout.tsx" if text != original else "NO_CHANGE frontend/src/app/layout.tsx")
print("GLOBAL_CLIENT_SUPPORT_WIDGET_INSTALLED")