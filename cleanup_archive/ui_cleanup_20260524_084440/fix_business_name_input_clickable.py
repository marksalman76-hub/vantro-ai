from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_business_name_input_clickable_{stamp}.tsx"
shutil.copy2(PAGE, backup)

text = PAGE.read_text(encoding="utf-8")

old = '''                <textarea
                  placeholder={String(value)}
                  value={businessProfile[String(key)] || ""}
                  onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [String(key)]: e.target.value }))}
                  rows={String(key) === "business_name" ? 1 : 2}
                  style={{
                    width: "100%",
                    resize: "vertical",
                    minHeight: String(key) === "business_name" ? 38 : 52,
                    border: "1px solid rgba(79,70,229,.14)",
                    background: "#fff",
                    padding: "9px 10px",
                    borderRadius: 10,
                    fontSize: 12.4,
                    lineHeight: 1.38,
                    color: "var(--color-dark)",
                    outline: "none",
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                    marginTop: 8,
                  }}
                />'''

new = '''                {String(key) === "business_name" ? (
                  <input
                    type="text"
                    placeholder="Type business name here"
                    value={businessProfile.business_name || ""}
                    onChange={(e) => setBusinessProfile((prev) => ({ ...prev, business_name: e.target.value }))}
                    onClick={(e) => e.currentTarget.focus()}
                    style={{
                      width: "100%",
                      height: 42,
                      border: "1.5px solid rgba(79,70,229,.35)",
                      background: "#fff",
                      padding: "9px 11px",
                      borderRadius: 10,
                      fontSize: 13,
                      color: "var(--color-dark)",
                      outline: "none",
                      boxSizing: "border-box",
                      fontFamily: "inherit",
                      marginTop: 8,
                      cursor: "text",
                      position: "relative",
                      zIndex: 5,
                    }}
                  />
                ) : (
                  <textarea
                    placeholder={String(value)}
                    value={businessProfile[String(key)] || ""}
                    onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [String(key)]: e.target.value }))}
                    rows={2}
                    style={{
                      width: "100%",
                      resize: "vertical",
                      minHeight: 52,
                      border: "1px solid rgba(79,70,229,.18)",
                      background: "#fff",
                      padding: "9px 10px",
                      borderRadius: 10,
                      fontSize: 12.4,
                      lineHeight: 1.38,
                      color: "var(--color-dark)",
                      outline: "none",
                      boxSizing: "border-box",
                      fontFamily: "inherit",
                      marginTop: 8,
                      cursor: "text",
                    }}
                  />
                )}'''

if old not in text:
    raise RuntimeError("Current textarea block not found. No changes written.")

text = text.replace(old, new, 1)

PAGE.write_text(text, encoding="utf-8")

print("BUSINESS_NAME_INPUT_CLICKABLE_FIXED")
print(f"Backup: {backup}")