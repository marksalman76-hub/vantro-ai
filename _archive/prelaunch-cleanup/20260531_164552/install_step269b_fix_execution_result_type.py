from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step269b_type_fix_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
'''type ExecutionResult = {
  success?: boolean;
  status?: string;
  workflow?: any;
  output?: any;
  approval?: any;
  message?: string;
};''',
'''type ExecutionResult = {
  success?: boolean;
  status?: string;
  workflow?: any;
  output?: any;
  approval?: any;
  message?: string;
  selected_agent_count?: number;
  results?: any[];
};'''
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_269B_EXECUTION_RESULT_TYPE_FIXED")
print(f"Backup: {backup}")
print("STEP_269B_OK")