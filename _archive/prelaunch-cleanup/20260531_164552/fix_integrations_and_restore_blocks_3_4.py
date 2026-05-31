from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_integrations_blocks_3_4_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# Remove overly broad dark-mode override.
s = re.sub(
    r'\n\s*\{/\* DARK_MODE_HALF_HALF_CARD_FIX_V1 \*/\}\s*<style>\{`.*?`\}</style>\s*',
    "\n",
    s,
    flags=re.DOTALL,
)

# Make integrations clickable.
old = '''{[
            ["E", "Email"],
            ["C", "CRM"],
            ["E", "Ecommerce Store"],
            ["W", "Website / CMS"],
            ["C", "Calendar"],
            ["S", "SMS / Phone"],
          ].map(([letter, label]) => (
            <button
              key={label}
              type="button"'''

new = '''{[
            ["email", "E", "Email"],
            ["crm", "C", "CRM"],
            ["store", "E", "Ecommerce Store"],
            ["website", "W", "Website / CMS"],
            ["calendar", "C", "Calendar"],
            ["sms", "S", "SMS / Phone"],
          ].map(([integrationKey, letter, label]) => (
            <button
              key={label}
              type="button"
              onClick={() => {
                const integration = DEFAULT_CLIENT_INTEGRATIONS.find((item) => item.integration_key === integrationKey);
                if (integration) {
                  connectIntegration(integration);
                }
              }}'''

if old not in s:
    raise SystemExit("FAILED: integrations map marker not found")
s = s.replace(old, new, 1)

# Add action to Add integration button.
old = '''<button
            type="button"
            style={{
              border: "1px solid #d8dcff",'''

new = '''<button
            type="button"
            onClick={() => {
              loadIntegrations();
              setIntegrationMessage("Choose an integration pill to connect a provider.");
            }}
            style={{
              border: "1px solid #d8dcff",'''

if old not in s:
    raise SystemExit("FAILED: add integration button marker not found")
s = s.replace(old, new, 1)

# Restore blocks 03 and 04 before bottom Activity section.
blocks = r'''
        <section style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch", marginBottom: 20 }}>
          <div style={{ ...cardStyle, minHeight: 230 }}>
            <StepHeader number="03" title="Review & approvals" />
            <h3 style={cardTitle}>Approval control</h3>
            <p style={mutedText}>
              Review generated deliverables before commercial use. Approve outputs or request changes while keeping execution governed.
            </p>

            <div style={{ display: "grid", gap: 9, marginTop: 14 }}>
              {[
                ["Client review", reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Pending"],
                ["Owner-safe controls", "Active"],
                ["High-risk actions", "Approval gated"],
              ].map(([label, value]) => (
                <div
                  key={label}
                  style={{
                    border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #e5eaf2",
                    background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",
                    borderRadius: 14,
                    padding: "10px 12px",
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 12,
                    color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",
                  }}
                >
                  <span style={{ fontWeight: 850 }}>{label}</span>
                  <span style={{ color: darkModeEnabled ? "#a5b4fc" : "var(--color-brand)", fontWeight: 900 }}>{value}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ ...cardStyle, minHeight: 230 }}>
            <StepHeader number="04" title="Optimisation & delivery" />
            <h3 style={cardTitle}>Delivery readiness</h3>
            <p style={mutedText}>
              Prepare approved outputs for next-step optimisation, asset review, and client-ready delivery.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 10, marginTop: 14 }}>
              {[
                ["Quality", "Checked"],
                ["Assets", attachedAssets.length ? `${attachedAssets.length}` : "Pending"],
                ["Next step", reviewStatus === "approved" ? "Optimise" : "Review"],
              ].map(([label, value]) => (
                <div
                  key={label}
                  style={{
                    border: darkModeEnabled ? "1px solid rgba(99,102,241,.24)" : "1px solid #e5eaf2",
                    background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",
                    borderRadius: 16,
                    padding: 12,
                    minHeight: 74,
                  }}
                >
                  <div style={{ fontSize: 11, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontWeight: 850 }}>{label}</div>
                  <div style={{ marginTop: 8, color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)", fontWeight: 950 }}>{value}</div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 12, color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)", fontSize: 11.5, fontWeight: 750 }}>
              Delivery remains governed and client-safe.
            </div>
          </div>
        </section>
'''

marker = '''        <section className="client-bottom-workspace" style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>'''

if "Review & approvals" not in s:
    if marker not in s:
        raise SystemExit("FAILED: bottom workspace marker not found")
    s = s.replace(marker, blocks + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("INTEGRATIONS_CLICKABLE_AND_BLOCKS_3_4_RESTORED")
print(f"Backup: {backup}")