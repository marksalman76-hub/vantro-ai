from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_broken_before_header_menu_build_fix_{stamp}.tsx"
shutil.copy2(PAGE, backup)

# Restore locked good page from last confirmed compact Business Profile commit.
good = subprocess.check_output(
    ["git", "show", "fad6cca:frontend/src/app/client/page.tsx"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
)
text = good

# Imports
if 'useState' not in text:
    text = text.replace(
        'import React from "react";',
        'import React, { useEffect, useState } from "react";',
    )
    text = text.replace(
        "import React from 'react';",
        "import React, { useEffect, useState } from 'react';",
    )

if "lucide-react" in text:
    text = re.sub(
        r'import\s+\{([^}]+)\}\s+from\s+["\']lucide-react["\'];',
        lambda m: 'import { ' + ", ".join(sorted(set(
            [x.strip() for x in m.group(1).split(",") if x.strip()] +
            ["Bell", "Settings", "User", "KeyRound", "ShieldCheck", "Moon", "Sun", "LogOut"]
        ))) + ' } from "lucide-react";',
        text,
        count=1,
    )
else:
    text = text.replace(
        "\n\n",
        '\nimport { Bell, Settings, User, KeyRound, ShieldCheck, Moon, Sun, LogOut } from "lucide-react";\n\n',
        1,
    )

component = r'''
function ClientHeaderAccountMenu() {
  const [open, setOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const workspaceActive = true;
  const accountState = workspaceActive ? "ACTIVE" : "INACTIVE";
  const statusDotClass = workspaceActive ? "bg-emerald-500" : "bg-red-500";

  useEffect(() => {
    if (darkMode) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  }, [darkMode]);

  return (
    <div className="relative flex items-center gap-3">
      <button className="rounded-2xl bg-slate-950 px-6 py-4 text-sm font-black text-white shadow-sm transition hover:bg-slate-800">
        + New execution
      </button>

      <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-5 py-4 text-sm font-black uppercase text-slate-950 shadow-sm">
        <span className={`h-2.5 w-2.5 rounded-full ${statusDotClass}`} />
        {accountState}
      </div>

      <button type="button" aria-label="Notifications" className="rounded-2xl border border-slate-200 bg-white p-4 text-slate-950 shadow-sm transition hover:bg-slate-50">
        <Bell className="h-5 w-5" />
      </button>

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-950 text-base font-black text-white shadow-sm transition hover:bg-slate-800"
      >
        PD
      </button>

      {open ? (
        <div className="absolute right-0 top-16 z-50 w-72 rounded-2xl border border-slate-200 bg-white p-4 text-slate-950 shadow-2xl">
          <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-950 text-base font-black text-white">PD</div>
            <div>
              <div className="text-base font-black">PD</div>
              <div className="text-xs font-semibold text-slate-500">pd@trance-formation.com.au</div>
              <div className="mt-1 flex items-center gap-2 text-xs font-bold text-slate-600">
                <span className={`h-2.5 w-2.5 rounded-full ${statusDotClass}`} />
                {accountState}
                <span>•</span>
                <span>Paid plan</span>
              </div>
            </div>
          </div>

          <div className="space-y-1 border-b border-slate-100 py-3">
            <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-bold hover:bg-slate-50"><Settings className="h-4 w-4" /> Settings</button>
            <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-bold hover:bg-slate-50"><User className="h-4 w-4" /> Profile</button>
            <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-bold hover:bg-slate-50"><KeyRound className="h-4 w-4" /> Password reset</button>
            <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-bold hover:bg-slate-50"><ShieldCheck className="h-4 w-4" /> 2FA</button>
          </div>

          <div className="flex items-center justify-between border-b border-slate-100 py-3">
            <div className="flex items-center gap-3 text-sm font-bold">
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              {darkMode ? "Light mode" : "Dark mode"}
            </div>
            <button type="button" onClick={() => setDarkMode((value) => !value)} className={`relative h-7 w-12 rounded-full transition ${darkMode ? "bg-slate-950" : "bg-slate-300"}`}>
              <span className={`absolute top-1 h-5 w-5 rounded-full bg-white shadow transition ${darkMode ? "left-6" : "left-1"}`} />
            </button>
          </div>

          <button className="mt-3 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-bold text-red-600 hover:bg-red-50">
            <LogOut className="h-4 w-4" /> Sign out
          </button>
        </div>
      ) : null}
    </div>
  );
}
'''

text = re.sub(r'\nexport\s+default\s+function\s+', "\n" + component + "\n\nexport default function ", text, count=1)

# Replace only the original header action group.
idx = text.find("+ New execution")
start = text.rfind("<div", 0, idx)
end = text.find("</div>", idx)

for _ in range(5):
    end = text.find("</div>", end + 6)

text = text[:start] + "<ClientHeaderAccountMenu />" + text[end + 6:]

# Ready for execution dot green.
text = re.sub(
    r'(Ready for execution[\s\S]{0,900}?)(bg-(?:blue|indigo|violet|purple|slate|gray)-[0-9]{2,3})',
    r'\1bg-emerald-500',
    text,
    count=1,
)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_HEADER_ACCOUNT_MENU_BUILD_FIXED")
print(f"Backup: {backup}")
print("Restored from fad6cca first, then safely applied header menu.")