from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_top_execution_area_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

# Remove detached governed footer if present anywhere below the flow.
src = re.sub(
    r'\n\s*<div className="[^"]*">\s*<div className="[^"]*">[\s\S]*?Governed execution, every time\.[\s\S]*?</div>\s*</div>\s*',
    "\n",
    src,
    flags=re.MULTILINE,
)

new_top = r'''        <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
          <section className="rounded-[28px] border border-slate-200/80 bg-white p-6 shadow-[0_18px_60px_rgba(15,23,42,0.06)]">
            <div className="mb-5 flex items-center gap-3">
              <span className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-bold text-indigo-600">01</span>
              <span className="text-sm font-black uppercase tracking-[0.18em] text-indigo-600">Run AI Agent</span>
            </div>

            <h2 className="text-2xl font-black tracking-tight text-slate-950">Select agents and launch governed execution.</h2>

            <div className="mt-5 grid gap-4 lg:grid-cols-[0.74fr_1.26fr]">
              <div>
                <div className="mb-2 text-sm font-black text-slate-600">Active agents</div>
                <div className="max-h-[372px] space-y-2 overflow-y-auto pr-2">
                  {[
                    "Product Research Agent",
                    "Product Copywriting Agent",
                    "UGC Creative Agent",
                    "Product Image Agent",
                    "CRM AI Agent",
                    "Influencer Outreach Agent",
                    "Analytics Optimisation Agent",
                    "Email Reply Agent",
                    "Social Media Content Agent"
                  ].map((agentName) => (
                    <button
                      key={agentName}
                      type="button"
                      className="flex w-full items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-black text-slate-950 shadow-sm transition hover:border-indigo-200 hover:bg-indigo-50/40"
                    >
                      <span className="flex items-center gap-2">
                        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                        {agentName}
                      </span>
                      <span className="text-[10px] font-black uppercase tracking-[0.12em] text-emerald-600">Active</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <div className="mb-2 text-sm font-black text-slate-600">Task</div>
                <textarea
                  className="min-h-[274px] w-full resize-none rounded-[22px] border border-slate-200 bg-white p-5 text-sm font-medium leading-6 text-slate-900 shadow-inner outline-none transition placeholder:text-slate-400 focus:border-indigo-300 focus:ring-4 focus:ring-indigo-100"
                  defaultValue={"Create a client-specific deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements."}
                />
                <button
                  type="button"
                  className="mt-4 flex h-14 w-full items-center justify-center rounded-[22px] bg-gradient-to-r from-indigo-600 to-cyan-500 text-sm font-black text-white shadow-[0_18px_45px_rgba(79,70,229,0.22)] transition hover:-translate-y-0.5"
                >
                  ✨ Run Agent
                </button>
              </div>
            </div>

            <div className="mt-4 text-sm font-medium text-slate-500">ⓘ Runs use your saved business profile.</div>
          </section>

          <section className="rounded-[28px] border border-slate-200/80 bg-white p-6 shadow-[0_18px_60px_rgba(15,23,42,0.06)]">
            <div className="mb-5 flex items-center gap-3">
              <span className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-bold text-indigo-600">02</span>
              <span className="text-sm font-black uppercase tracking-[0.18em] text-indigo-600">Live Execution Flow</span>
            </div>

            <h2 className="text-2xl font-black tracking-tight text-slate-950">Execution pipeline</h2>
            <p className="mt-1 text-sm font-medium text-slate-500">Every AI deliverable flows through approval, optimisation, workflow validation, and governed execution before deployment.</p>

            <div className="mt-5 rounded-[24px] border border-slate-200 bg-slate-50/70 p-4">
              <div className="space-y-3">
                {[
                  ["1", "Execution requested", "Started", "Live"],
                  ["2", "Business profile applied", "Client context loaded", "Live"],
                  ["3", "Deliverable status", "Ready", "Live"],
                  ["4", "Client review", "Pending", "Open"],
                  ["5", "Execution ready", "Output routing prepared", "Next"]
                ].map(([step, title, detail, state]) => (
                  <div key={step} className="flex items-center gap-4 rounded-[20px] border border-slate-200 bg-white p-4 shadow-sm">
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-black text-white ${step === "5" ? "bg-cyan-500" : "bg-indigo-600"}`}>
                      {step}
                    </div>
                    <div className="min-w-0 flex-1 rounded-[18px] border border-slate-200 bg-white px-4 py-3 shadow-[0_10px_35px_rgba(15,23,42,0.04)]">
                      <div className="text-sm font-black text-slate-950">{title}</div>
                      <div className="mt-0.5 text-xs font-semibold text-slate-500">{detail}</div>
                    </div>
                    <div className="w-12 text-right text-sm font-medium text-slate-500">{state}</div>
                  </div>
                ))}

                <div className="rounded-[22px] border border-indigo-100 bg-indigo-50/80 p-4">
                  <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white text-indigo-600 shadow-sm">✦</div>
                    <div>
                      <div className="text-sm font-black text-slate-950">Governed execution, every time.</div>
                      <div className="mt-1 text-sm font-medium text-slate-600">All steps are tracked, logged, quality-checked, and routed through the correct approval controls.</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>'''

pattern = re.compile(
    r'\s*<div className="grid gap-5 xl:grid-cols-\[1fr_1fr\]">[\s\S]*?<span className="text-sm font-black uppercase tracking-\[0\.18em\] text-indigo-600">Run AI Agent</span>[\s\S]*?<span className="text-sm font-black uppercase tracking-\[0\.18em\] text-indigo-600">Live Execution Flow</span>[\s\S]*?</div>\s*(?=<div className="grid gap-5 xl:grid-cols-\[1fr_1fr\]">|\n\s*<section|\n\s*</main>)',
    re.MULTILINE,
)

matches = list(pattern.finditer(src))
if not matches:
    raise SystemExit("ERROR: Could not find top Run AI Agent / Live Execution Flow block. No changes made.")

m = matches[0]
src = src[:m.start()] + "\n" + new_top + "\n" + src[m.end():]

PAGE.write_text(src, encoding="utf-8")

print("TOP_RUN_AGENT_AND_LIVE_EXECUTION_FLOW_FIXED")
print(f"Backup: {backup}")
print("Updated: frontend/src/app/client/page.tsx")