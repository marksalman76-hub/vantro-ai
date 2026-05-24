from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_blocks_1_2_dark_add_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# Make + Add integration clickable.
old = '''<button
            type="button"
            onClick={() => {
              loadIntegrations();
              setIntegrationMessage("Choose an integration pill to connect a provider.");
            }}
            style={{
              border: "1px solid #d8dcff",'''

new = '''<button
            type="button"
            onClick={() => {
              const providerName = window.prompt("Which integration would you like to add? Example: Ads, Analytics, Social Media, Shopify, HubSpot");
              if (!providerName || !providerName.trim()) return;
              setIntegrationMessage(`${providerName.trim()} integration request noted. Connection setup will open once this provider is enabled.`);
              setToastMessage(`${providerName.trim()} integration request noted.`);
            }}
            style={{
              border: "1px solid #d8dcff",'''

if old not in s:
    raise SystemExit("FAILED: add integration button marker not found")
s = s.replace(old, new, 1)

# Add targeted dark polish for Blocks 01/02 and integration row.
insert = r'''
        {/* TARGETED_DARK_MODE_BLOCKS_1_2_POLISH_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            main section:nth-of-type(5),
            main section:nth-of-type(6) {
              background: linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98)) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 24px 80px rgba(0,0,0,.34) !important;
            }

            main section:nth-of-type(5) [style*="background: #fff"],
            main section:nth-of-type(5) [style*="background: rgb(255, 255, 255)"],
            main section:nth-of-type(5) [style*="background: #ffffff"],
            main section:nth-of-type(6) [style*="background: #fff"],
            main section:nth-of-type(6) [style*="background: rgb(255, 255, 255)"],
            main section:nth-of-type(6) [style*="background: #ffffff"] {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 12px 32px rgba(0,0,0,.22) !important;
            }

            main section:nth-of-type(5) textarea,
            main section:nth-of-type(5) input,
            main section:nth-of-type(6) textarea,
            main section:nth-of-type(6) input {
              background: rgba(3,10,24,.88) !important;
              border-color: rgba(129,140,248,.34) !important;
              color: #f8fafc !important;
            }

            main section:nth-of-type(5) [style*="linear-gradient(135deg,#eff6ff,#ffffff)"],
            main section:nth-of-type(6) [style*="linear-gradient(135deg,#eff6ff,#ffffff)"],
            main section:nth-of-type(5) [style*="linear-gradient(135deg,#eff6ff,#ffffff)"] * {
              background: rgba(12,24,49,.92) !important;
              color: #f8fafc !important;
            }

            main section:nth-of-type(5) [style*="color: var(--color-dark)"],
            main section:nth-of-type(5) [style*="color: #0f172a"],
            main section:nth-of-type(6) [style*="color: var(--color-dark)"],
            main section:nth-of-type(6) [style*="color: #0f172a"] {
              color: #f8fafc !important;
            }

            main section:nth-of-type(5) [style*="color: var(--color-muted)"],
            main section:nth-of-type(5) [style*="color: #64748b"],
            main section:nth-of-type(6) [style*="color: var(--color-muted)"],
            main section:nth-of-type(6) [style*="color: #64748b"] {
              color: #94a3b8 !important;
            }

            main section:nth-of-type(4) button {
              pointer-events: auto !important;
              cursor: pointer !important;
            }
          ` : ``}
        `}</style>
'''

marker = '''        <section style={responsiveWorkspaceGridStyle}>'''

if "TARGETED_DARK_MODE_BLOCKS_1_2_POLISH_V1" not in s:
    if marker not in s:
        raise SystemExit("FAILED: blocks 1/2 marker not found")
    s = s.replace(marker, insert + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("BLOCKS_1_2_DARK_AND_ADD_INTEGRATION_FIXED")
print(f"Backup: {backup}")