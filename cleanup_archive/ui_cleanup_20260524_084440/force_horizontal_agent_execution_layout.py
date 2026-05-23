from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_horizontal_agent_execution_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

effect_marker = "  useEffect(() => {\n    fetch(\"/api/client-me\")"

horizontal_effect = r'''
  useEffect(() => {
    const applyHorizontalExecutionLayout = () => {
      const headings = Array.from(document.querySelectorAll("h1,h2,h3,div,p,span,label"));
      const activeAgentsLabel = headings.find((node) => node.textContent?.trim() === "Active agents");

      if (!activeAgentsLabel) return;

      const runCard =
        activeAgentsLabel.closest("section") ||
        activeAgentsLabel.closest("div");

      if (!runCard) return;

      const possibleLists = Array.from(runCard.querySelectorAll("div")).filter((node) => {
        const text = node.textContent || "";
        return text.includes("Head Agent") && text.includes("Strategist Agent");
      });

      const agentList = possibleLists[possibleLists.length - 1] as HTMLElement | undefined;

      if (agentList) {
        agentList.style.display = "flex";
        agentList.style.flexDirection = "row";
        agentList.style.flexWrap = "nowrap";
        agentList.style.gap = "8px";
        agentList.style.overflowX = "auto";
        agentList.style.overflowY = "hidden";
        agentList.style.maxHeight = "76px";
        agentList.style.paddingBottom = "6px";
        agentList.style.alignItems = "center";

        Array.from(agentList.children).forEach((child) => {
          const item = child as HTMLElement;
          item.style.flex = "0 0 auto";
          item.style.minWidth = "170px";
          item.style.maxWidth = "220px";
          item.style.padding = "8px 10px";
          item.style.borderRadius = "12px";
          item.style.whiteSpace = "nowrap";
          item.style.overflow = "hidden";
          item.style.textOverflow = "ellipsis";
        });
      }

      const taskLabel = headings.find((node) => node.textContent?.trim() === "Task");
      const taskCard = taskLabel?.parentElement?.querySelector("textarea, div") as HTMLElement | null;

      if (taskCard) {
        taskCard.style.minHeight = "96px";
      }
    };

    applyHorizontalExecutionLayout();
    window.setTimeout(applyHorizontalExecutionLayout, 300);
  }, [selectedAgents]);
'''

if horizontal_effect.strip() not in text:
    if effect_marker not in text:
        raise SystemExit("Could not find safe insertion point for horizontal execution layout effect.")
    text = text.replace(effect_marker, horizontal_effect + "\n" + effect_marker, 1)

# Reduce lower card height/spacing globally without touching locked business profile layout.
text = text.replace('minHeight: 190,', 'minHeight: 120,')
text = text.replace('minHeight: 180,', 'minHeight: 120,')
text = text.replace('height: 64,', 'height: 52,')
text = text.replace('minHeight: 64,', 'minHeight: 52,')

path.write_text(text, encoding="utf-8")

print("HORIZONTAL_AGENT_EXECUTION_LAYOUT_FIXED")
print(f"Backup: {backup}")