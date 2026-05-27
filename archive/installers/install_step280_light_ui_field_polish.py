from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step280_field_polish_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace("minHeight: 58,", "minHeight: 72,")
text = text.replace('padding: "12px 14px"', 'padding: "13px 15px"')
text = text.replace('border: "1px solid #dbe3ee"', 'border: "1px solid #d7e0ec"')
text = text.replace('lineHeight: 1.45,', 'lineHeight: 1.5,')
text = text.replace('rows={2}', 'rows={3}')

# Add scrollbar hiding style to textarea fields
text = text.replace(
'''                  style={input}
                />''',
'''                  style={{
                    ...input,
                    scrollbarWidth: "none",
                  }}
                />'''
)

text = text.replace(
'''                style={{ ...input, minHeight: 132, fontSize: 14 }}
              />''',
'''                style={{
                  ...input,
                  minHeight: 138,
                  fontSize: 14,
                  scrollbarWidth: "none",
                }}
              />'''
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_280_LIGHT_UI_FIELD_POLISH_INSTALLED")
print(f"Backup: {backup}")
print("STEP_280_OK")