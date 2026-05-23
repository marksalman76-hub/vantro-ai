from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUP_DIR / f"client_page_before_execution_workspace_both_columns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

old_footer_patterns = [
    r'\n\s*<div className="[^"]*">\s*<div className="[^"]*">[^\n]*Governed execution, every time\.[\s\S]*?</div>\s*</div>\s*',
    r'\n\s*<section className="[^"]*">[\s\S]*?Governed execution, every time\.[\s\S]*?</section>\s*',
]

for pattern in old_footer_patterns:
    src = re.sub(pattern, "\n", src, flags=re.MULTILINE)

execution_workspace = r'''          <section className="rounded-[28px] border border-slate-200/80 bg-white p-6 shadow-[0_18px_60px_rgba(15,23,42,0.06)]">
            <div className="mb-5 flex items-center gap-3">
              <span className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-bold text-indigo-600">02</span>
              <span className="text-sm font-black uppercase tracking-[0.18em] text-indigo-600">Execution Workspace</span>
            </div>

            <div className="grid gap-5 lg:grid-cols-[0.92fr_1.08fr]">
              <div className="rounded-[24px] border border-slate-200 bg-slate-50/70 p-4">
                <div className="mb-4 flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-xl font-black text-slate-950">Agent runtime console</h3>
                    <p className="mt-1 text-sm font-medium text-slate-500">Choose the specialist agent for this execution.</p>
                  </div>
                  <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-black uppercase tracking-[0.12em] text-emerald-700">Live</span>
                </div>

                <div className="max-h-[430px] space-y-3 overflow-y-auto pr-2">
                  {[
                    ["Product Copywriting Agent", "Conversion copy, product pages, offers", "ACTIVE"],
                    ["UGC Creative Agent", "Scripts, hooks, creator briefs", "ACTIVE"],
                    ["Product Image Agent", "Image direction and asset briefs", "ACTIVE"],
                    ["Influencer Outreach Agent", "Creator fit, outreach, follow-up", "ACTIVE"],
                    ["Analytics Optimisation Agent", "Performance insights and next actions", "ACTIVE"],
                    ["Email Reply Agent", "Inbound and outbound response support", "ACTIVE"],
                    ["CRM AI Agent", "Pipeline, follow-up, segmentation", "ACTIVE"],
                    ["Head Agent", "Enterprise oversight and recommendations", "ENTERPRISE"]
                  ].map(([name, detail, status]) => (
                    <button
                      key={name}
                      type="button"
                      className="group w-full rounded-[20px] border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="text-sm font-black text-slate-950">{name}</div>
                          <div className="mt-1 text-xs font-semibold text-slate-500">{detail}</div>
                        </div>
                        <span className={`mt-1 h-3 w-3 shrink-0 rounded-full ${status === "ACTIVE" ? "bg-emerald-500" : "bg-rose-500"}`} />
                      </div>
                      <div className="mt-3 inline-flex rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-black uppercase tracking-[0.12em] text-slate-500">
                        {status}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="rounded-[24px] border border-slate-200 bg-slate-50/70 p-4">
                <div className="mb-4 flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-xl font-black text-slate-950">Execution pipeline</h3>
                    <p className="mt-1 text-sm font-medium text-slate-500">Tracked, governed workflow from request to deliverable.</p>
                  </div>
                  <span className="rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-black uppercase tracking-[0.12em] text-indigo-700">Ready</span>
                </div>

                <div className="space-y-3">
                  {[
                    ["1", "Business profile loaded", "Saved context applied"],
                    ["2", "Agent selected", "Specialist runtime prepared"],
                    ["3", "Quality gate active", "Premium output checks enabled"],
                    ["4", "Execution ready", "Next"],
                    ["5", "Deliverable routing", "Output, approval, and history logging"]
                  ].map(([step, title, detail]) => (
                    <div key={step} className="flex items-center gap-4 rounded-[20px] border border-slate-200 bg-white p-4 shadow-sm">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-cyan-500 text-sm font-black text-white">
                        {step}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-black text-slate-950">{title}</div>
                        <div className="mt-0.5 text-xs font-semibold text-slate-500">{detail}</div>
                      </div>
                      <div className="h-2 w-2 rounded-full bg-slate-300" />
                    </div>
                  ))}

                  <div className="rounded-[22px] border border-indigo-100 bg-indigo-50/70 p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-indigo-600 shadow-sm">✦</div>
                      <div>
                        <div className="text-sm font-black text-slate-950">Governed execution, every time.</div>
                        <div className="mt-1 text-sm font-medium text-slate-600">All steps are tracked, logged, quality-checked, and routed through the correct approval controls.</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>'''

pattern = re.compile(
    r'\s*<section className="[^"]*">\s*<div className="mb-5 flex items-center gap-3">[\s\S]*?<span className="text-sm font-black uppercase tracking-\[0\.18em\] text-indigo-600">Execution Workspace</span>[\s\S]*?</section>',
    re.MULTILINE
)

matches = list(pattern.finditer(src))
if not matches:
    raise SystemExit("ERROR: Could not find Execution Workspace section. No changes made.")

m = matches[0]
src = src[:m.start()] + "\n" + execution_workspace + "\n" + src[m.end():]

PAGE.write_text(src, encoding="utf-8")

print("EXECUTION_WORKSPACE_BOTH_COLUMNS_FIXED")
print(f"Backup: {backup}")
print("Updated: frontend/src/app/client/page.tsx")