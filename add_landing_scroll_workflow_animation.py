from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"landing_page_before_scroll_workflow_animation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

component = r'''
function AnimatedWorkflowSection() {
  const steps = [
    ["01", "Client context", "Business profile, offer, audience, products and goals are converted into execution-ready intelligence."],
    ["02", "Agent selection", "Specialist ecommerce agents activate based on the task, purchased access and client workflow needs."],
    ["03", "Premium output", "Agents generate commercial-grade deliverables, campaign assets, copy, strategy and execution recommendations."],
    ["04", "Governed delivery", "High-risk actions stay approval-gated while safe execution moves through the workflow with audit visibility."],
  ];

  return (
    <section className="animatedWorkflowSection">
      <motion.div
        className="workflowHeader"
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.26 }}
        transition={{ duration: 0.72 }}
      >
        <div className="runtimeEyebrow">Workflow intelligence</div>
        <h2>From business context to governed execution.</h2>
        <p>
          The landing page now shows the product as an active AI workforce system:
          context enters, agents collaborate, outputs are produced, and risky actions
          stay under approval control.
        </p>
      </motion.div>

      <div className="workflowStage">
        {steps.map(([number, title, body], index) => (
          <motion.div
            key={title}
            className="workflowStep"
            initial={{ opacity: 0, x: index % 2 === 0 ? -36 : 36, y: 22 }}
            whileInView={{ opacity: 1, x: 0, y: 0 }}
            viewport={{ once: true, amount: 0.34 }}
            transition={{ duration: 0.66, delay: index * 0.09, ease: [0.22, 1, 0.36, 1] }}
            whileHover={{ y: -8, scale: 1.015 }}
          >
            <div className="workflowNumber">{number}</div>
            <div>
              <strong>{title}</strong>
              <span>{body}</span>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="workflowConsole"
        initial={{ opacity: 0, y: 38, scale: 0.98 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ once: true, amount: 0.24 }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="workflowConsoleTop">
          <span />
          <span />
          <span />
          <strong>Live AI execution preview</strong>
        </div>

        <div className="workflowConsoleBody">
          {[
            ["Business intelligence", "Loaded", "100%"],
            ["Agent workflow", "Running", "76%"],
            ["Premium output", "Generating", "64%"],
            ["Approval controls", "Active", "Locked"],
          ].map(([label, status, value]) => (
            <div key={label} className="consoleRow">
              <div>
                <strong>{label}</strong>
                <span>{status}</span>
              </div>
              <em>{value}</em>
            </div>
          ))}
        </div>
      </motion.div>
    </section>
  );
}
'''

css = r'''
        /* LANDING_SCROLL_WORKFLOW_ANIMATION_V1 */
        .animatedWorkflowSection{
          max-width:1180px;
          margin:32px auto 0;
          padding:70px 24px;
          position:relative;
          z-index:2;
        }
        .animatedWorkflowSection:before{
          content:"";
          position:absolute;
          left:50%;
          top:180px;
          bottom:140px;
          width:1px;
          background:linear-gradient(180deg,transparent,rgba(124,116,255,.42),rgba(14,207,188,.28),transparent);
          opacity:.8;
        }
        .workflowHeader{
          max-width:820px;
          margin:0 auto 42px;
          text-align:center;
        }
        .workflowHeader h2{
          margin:0;
          color:#fff;
          font-size:clamp(34px,5vw,62px);
          line-height:.98;
          letter-spacing:-.06em;
        }
        .workflowHeader p{
          margin:18px auto 0;
          max-width:720px;
          color:#A7B0C6;
          line-height:1.65;
          font-size:16px;
        }
        .workflowStage{
          display:grid;
          grid-template-columns:repeat(2,minmax(0,1fr));
          gap:18px;
          position:relative;
        }
        .workflowStep{
          min-height:168px;
          border-radius:28px;
          padding:24px;
          border:1px solid rgba(124,116,255,.22);
          background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.032));
          box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 24px 70px rgba(0,0,0,.22);
          backdrop-filter:blur(20px) saturate(150%);
          -webkit-backdrop-filter:blur(20px) saturate(150%);
          display:grid;
          grid-template-columns:56px 1fr;
          gap:18px;
          align-items:start;
        }
        .workflowNumber{
          width:52px;
          height:52px;
          display:grid;
          place-items:center;
          border-radius:18px;
          background:linear-gradient(135deg,rgba(124,116,255,.30),rgba(14,207,188,.14));
          color:#C7D2FE;
          font-weight:950;
          box-shadow:0 18px 44px rgba(91,82,240,.22);
        }
        .workflowStep strong{
          display:block;
          color:#fff;
          font-size:19px;
          letter-spacing:-.03em;
          margin-bottom:10px;
        }
        .workflowStep span{
          display:block;
          color:#A7B0C6;
          line-height:1.58;
          font-size:14.5px;
        }
        .workflowConsole{
          margin:26px auto 0;
          max-width:820px;
          border-radius:30px;
          overflow:hidden;
          border:1px solid rgba(124,116,255,.24);
          background:linear-gradient(180deg,rgba(9,15,31,.96),rgba(3,8,20,.98));
          box-shadow:0 38px 100px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.08);
        }
        .workflowConsoleTop{
          height:54px;
          display:flex;
          align-items:center;
          gap:9px;
          padding:0 18px;
          border-bottom:1px solid rgba(255,255,255,.08);
          background:rgba(255,255,255,.035);
          color:#CBD5E1;
          font-size:12px;
          font-weight:900;
          letter-spacing:.04em;
          text-transform:uppercase;
        }
        .workflowConsoleTop span{
          width:10px;
          height:10px;
          border-radius:99px;
          background:#7C74FF;
        }
        .workflowConsoleTop span:nth-child(2){background:#0ECFBC}
        .workflowConsoleTop span:nth-child(3){background:#F59E0B}
        .workflowConsoleTop strong{margin-left:8px}
        .workflowConsoleBody{
          display:grid;
          gap:10px;
          padding:18px;
        }
        .consoleRow{
          display:flex;
          justify-content:space-between;
          gap:16px;
          align-items:center;
          padding:14px 16px;
          border-radius:18px;
          border:1px solid rgba(124,116,255,.16);
          background:rgba(255,255,255,.045);
        }
        .consoleRow strong{
          display:block;
          color:#fff;
          font-size:14px;
          margin-bottom:3px;
        }
        .consoleRow span{
          color:#94A3B8;
          font-size:12px;
          font-weight:800;
        }
        .consoleRow em{
          font-style:normal;
          color:#0ECFBC;
          font-weight:950;
          font-size:13px;
        }
        @media(max-width:860px){
          .animatedWorkflowSection:before{display:none}
          .workflowStage{grid-template-columns:1fr}
        }
'''

if "function AnimatedWorkflowSection()" not in s:
    insert_at = s.find("export default")
    if insert_at == -1:
        raise SystemExit("FAILED: export default marker not found")
    s = s[:insert_at] + component + "\n" + s[insert_at:]

if "LANDING_SCROLL_WORKFLOW_ANIMATION_V1" not in s:
    marker = "        @media(max-width:900px)"
    if marker not in s:
        raise SystemExit("FAILED: CSS marker not found")
    s = s.replace(marker, css + "\n" + marker, 1)

if "<AnimatedWorkflowSection />" not in s:
    if "<LandingMotionRuntimeLayer />" in s:
        s = s.replace("<LandingMotionRuntimeLayer />", "<LandingMotionRuntimeLayer />\n\n      <AnimatedWorkflowSection />", 1)
    elif '<section className="pricing"' in s:
        s = s.replace('<section className="pricing"', '<AnimatedWorkflowSection />\n\n      <section className="pricing"', 1)
    else:
        raise SystemExit("FAILED: workflow insertion point not found")

TARGET.write_text(s, encoding="utf-8")

print("LANDING_SCROLL_WORKFLOW_ANIMATION_ADDED")
print(f"Backup: {backup}")