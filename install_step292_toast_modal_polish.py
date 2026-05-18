from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step292_toast_modal_polish_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

# Hide toast automatically after it appears
target = '''  const toggleAgent = (agent: string) => {'''
insert = '''  useEffect(() => {
    if (!toastMessage) return;

    const timer = window.setTimeout(() => {
      setToastMessage("");
    }, 3200);

    return () => window.clearTimeout(timer);
  }, [toastMessage]);

'''

if insert.strip() not in text:
    text = text.replace(target, insert + target)

# Hide toast immediately when opening rejection modal
text = text.replace(
'''                    onClick={() => {
                      setShowRejectModal(true);
                      setExecutionState("rejected");
                    }}''',
'''                    onClick={() => {
                      setToastMessage("");
                      setShowRejectModal(true);
                      setExecutionState("rejected");
                    }}'''
)

# Make toast not render when modal is open
text = text.replace(
'''      {toastMessage ? (''',
'''      {toastMessage && !showRejectModal ? ('''
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_292_TOAST_MODAL_POLISH_INSTALLED")
print(f"Backup: {backup}")
print("STEP_292_OK")