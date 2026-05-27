from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_premium_execution_section_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

effect = r'''
  useEffect(() => {
    const applyPremiumExecutionSectionLayout = () => {
      const allNodes = Array.from(document.querySelectorAll("section, div, h1, h2, h3, p, span, label, button, textarea"));

      const findByText = (exactText: string) =>
        allNodes.find((node) => node.textContent?.trim() === exactText) as HTMLElement | undefined;

      const findIncludes = (partialText: string) =>
        allNodes.find((node) => node.textContent?.includes(partialText)) as HTMLElement | undefined;

      const runHeading = findIncludes("Select agents and launch governed execution");
      const executionHeading = findByText("Execution pipeline");
      const activeAgentsLabel = findByText("Active agents");
      const taskLabel = findByText("Task");

      const runCard = runHeading?.closest("section") as HTMLElement | null;
      const executionCard = executionHeading?.closest("section") as HTMLElement | null;

      if (runCard) {
        runCard.style.padding = "24px";
        runCard.style.borderRadius = "28px";
        runCard.style.minHeight = "0";
        runCard.style.overflow = "hidden";
      }

      if (executionCard) {
        executionCard.style.padding = "24px";
        executionCard.style.borderRadius = "28px";
        executionCard.style.minHeight = "0";
        executionCard.style.overflow = "hidden";
      }

      if (activeAgentsLabel) {
        const activeAgentsArea = activeAgentsLabel.parentElement as HTMLElement | null;
        if (activeAgentsArea) {
          activeAgentsArea.style.display = "block";
          activeAgentsArea.style.marginBottom = "16px";
        }

        const candidateLists = Array.from((runCard || document).querySelectorAll("div")).filter((node) => {
          const content = node.textContent || "";
          return content.includes("Head Agent") && content.includes("Strategist Agent") && content.includes("Marketing Specialist");
        }) as HTMLElement[];

        const agentList = candidateLists[candidateLists.length - 1];

        if (agentList) {
          agentList.style.display = "flex";
          agentList.style.flexDirection = "row";
          agentList.style.flexWrap = "nowrap";
          agentList.style.gap = "10px";
          agentList.style.overflowX = "auto";
          agentList.style.overflowY = "hidden";
          agentList.style.maxHeight = "104px";
          agentList.style.padding = "4px 4px 12px";
          agentList.style.marginTop = "10px";
          agentList.style.alignItems = "stretch";
          agentList.style.scrollbarWidth = "thin";

          Array.from(agentList.children).forEach((child, index) => {
            const item = child as HTMLElement;
            item.style.flex = "0 0 178px";
            item.style.minWidth = "178px";
            item.style.maxWidth = "178px";
            item.style.minHeight = "74px";
            item.style.padding = "12px 12px";
            item.style.borderRadius = "16px";
            item.style.border = "1px solid rgba(79,70,229,.18)";
            item.style.background = "linear-gradient(180deg,#ffffff 0%,#f7f7ff 100%)";
            item.style.boxShadow = "0 12px 28px rgba(15,23,42,.06)";
            item.style.whiteSpace = "normal";
            item.style.overflow = "hidden";
            item.style.textOverflow = "ellipsis";
            item.style.color = "#111827";
            item.style.fontWeight = "850";
            item.style.fontSize = "12px";
            item.style.lineHeight = "1.25";
            item.style.display = "flex";
            item.style.alignItems = "center";
            item.style.gap = "10px";
            item.style.position = "relative";

            if (!item.querySelector("[data-agent-premium-icon='true']")) {
              const icon = document.createElement("span");
              icon.dataset.agentPremiumIcon = "true";
              icon.textContent = ["👤", "🎯", "📈", "📅", "📣", "✍️", "🔍", "✉️"][index % 8];
              icon.style.width = "34px";
              icon.style.height = "34px";
              icon.style.borderRadius = "999px";
              icon.style.display = "inline-flex";
              icon.style.alignItems = "center";
              icon.style.justifyContent = "center";
              icon.style.background = "linear-gradient(135deg,#4f46e5,#06b6d4)";
              icon.style.color = "#fff";
              icon.style.flex = "0 0 auto";
              item.prepend(icon);
            }

            if (!item.querySelector("[data-agent-premium-check='true']")) {
              const check = document.createElement("span");
              check.dataset.agentPremiumCheck = "true";
              check.textContent = "●";
              check.style.position = "absolute";
              check.style.top = "10px";
              check.style.right = "10px";
              check.style.color = "#22c55e";
              check.style.fontSize = "13px";
              item.appendChild(check);
            }
          });
        }
      }

      if (taskLabel) {
        const taskArea = taskLabel.parentElement as HTMLElement | null;
        if (taskArea) {
          taskArea.style.display = "block";
          taskArea.style.marginTop = "10px";
        }

        const taskText = Array.from((runCard || document).querySelectorAll("textarea, div")).find((node) =>
          node.textContent?.includes("Create a client-specific client deliverable")
        ) as HTMLElement | undefined;

        if (taskText) {
          taskText.style.width = "100%";
          taskText.style.minHeight = "118px";
          taskText.style.borderRadius = "18px";
          taskText.style.border = "1px solid #dbe3f0";
          taskText.style.padding = "16px";
          taskText.style.background = "#fff";
          taskText.style.boxSizing = "border-box";
          taskText.style.fontSize = "14px";
          taskText.style.lineHeight = "1.45";
        }
      }

      const runButton = Array.from((runCard || document).querySelectorAll("button")).find((button) =>
        button.textContent?.includes("Run Agent")
      ) as HTMLElement | undefined;

      if (runButton) {
        runButton.style.height = "56px";
        runButton.style.borderRadius = "18px";
        runButton.style.marginTop = "16px";
        runButton.style.boxShadow = "0 18px 36px rgba(6,182,212,.18)";
      }

      if (executionCard && !executionCard.querySelector("[data-premium-flow-proof='true']")) {
        const proof = document.createElement("div");
        proof.dataset.premiumFlowProof = "true";
        proof.innerHTML = `
          <div style="width:42px;height:42px;border-radius:16px;background:linear-gradient(135deg,#ede9fe,#f5f3ff);display:flex;align-items:center;justify-content:center;font-weight:900;color:#4f46e5;">✦</div>
          <div>
            <div style="font-weight:900;color:#0f172a;font-size:14px;">Governed execution, every time.</div>
            <div style="color:#64748b;font-size:13px;margin-top:3px;">All steps are tracked, logged, and optimised for quality and consistency.</div>
          </div>
        `;
        proof.style.display = "flex";
        proof.style.alignItems = "center";
        proof.style.gap = "14px";
        proof.style.marginTop = "26px";
        proof.style.padding = "18px";
        proof.style.borderRadius = "18px";
        proof.style.background = "linear-gradient(90deg,#f4f1ff,#f8fafc)";
        proof.style.border = "1px solid rgba(79,70,229,.08)";
        executionCard.appendChild(proof);
      }

      if (executionCard) {
        const rows = Array.from(executionCard.querySelectorAll("div")).filter((node) => {
          const content = node.textContent || "";
          return (
            content.includes("Execution requested") ||
            content.includes("Deliverable status") ||
            content.includes("Client review") ||
            content.includes("Execution ready")
          );
        }) as HTMLElement[];

        rows.forEach((row) => {
          const content = row.textContent || "";
          if (!content.includes("Started") && !content.includes("Ready") && !content.includes("Pending") && !content.includes("Next")) return;

          row.style.border = "1px solid #e5eaf2";
          row.style.borderRadius = "18px";
          row.style.padding = "12px 14px";
          row.style.marginBottom = "10px";
          row.style.background = "#fff";
          row.style.boxShadow = "0 10px 24px rgba(15,23,42,.04)";
        });
      }
    };

    applyPremiumExecutionSectionLayout();
    window.setTimeout(applyPremiumExecutionSectionLayout, 350);
    window.setTimeout(applyPremiumExecutionSectionLayout, 900);
  }, [selectedAgents, activeAccountPanel]);
'''

if "applyPremiumExecutionSectionLayout" in text:
    print("Premium execution layout effect already exists.")
else:
    marker = "  useEffect(() => {\n    fetch(\"/api/client-me\")"
    if marker not in text:
        raise SystemExit("Could not find safe insertion point for premium execution layout effect.")
    text = text.replace(marker, effect + "\n\n" + marker, 1)

path.write_text(text, encoding="utf-8")

print("PREMIUM_EXECUTION_SECTION_LAYOUT_APPLIED")
print(f"Backup: {backup}")