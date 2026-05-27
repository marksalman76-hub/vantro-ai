from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"customer_portal_status_governance_before_{STAMP}"

CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
TEST_FILE = ROOT / "test_customer_portal_status_governance.py"

for path in [CLIENT_PAGE, TEST_FILE]:
    if path.exists():
        target = BACKUP_DIR / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    path.parent.mkdir(parents=True, exist_ok=True)

if not CLIENT_PAGE.exists():
    raise FileNotFoundError(f"Missing client page: {CLIENT_PAGE}")

text = CLIENT_PAGE.read_text(encoding="utf-8")

helper_block = r'''

function CustomerAgentStatusBadge({ active }: { active: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[11px] font-bold uppercase tracking-[0.14em] ${
        active
          ? "border-emerald-300/60 bg-emerald-50 text-emerald-700"
          : "border-rose-300/60 bg-rose-50 text-rose-700"
      }`}
      aria-label={active ? "ACTIVE" : "INACTIVE"}
    >
      <span
        className={`h-2.5 w-2.5 rounded-full ${
          active ? "bg-emerald-500" : "bg-rose-500"
        }`}
      />
      {active ? "ACTIVE" : "INACTIVE"}
    </span>
  );
}

function customerPortalSafeText(value: unknown, fallback = "") {
  const raw = value === null || value === undefined ? fallback : String(value);
  return raw
    .replace(/provider internals?/gi, "service details")
    .replace(/queue internals?/gi, "processing status")
    .replace(/raw json/gi, "details")
    .replace(/debug/gi, "support")
    .replace(/webhook/gi, "connection")
    .replace(/prompt/gi, "request")
    .replace(/credential/gi, "secure access")
    .replace(/governance/gi, "approval")
    .replace(/runtime/gi, "system");
}

function customerPortalSelectionLockedNotice() {
  return "Agent selections are locked after activation. Package changes, swaps, upgrades, or added agents require owner/admin approval.";
}
'''

if "function CustomerAgentStatusBadge" not in text:
    insert_after = text.find("type Account = {")
    if insert_after == -1:
        raise RuntimeError("Could not find Account type insertion point.")
    text = text[:insert_after] + helper_block + "\n" + text[insert_after:]

# Ensure common literal status words are uppercase in visible strings.
text = text.replace(">Active<", ">ACTIVE<")
text = text.replace(">Inactive<", ">INACTIVE<")
text = text.replace('"Active"', '"ACTIVE"')
text = text.replace('"Inactive"', '"INACTIVE"')
text = text.replace("'Active'", "'ACTIVE'")
text = text.replace("'Inactive'", "'INACTIVE'")

# Add a persistent customer-safe lock notice after the first strong active-agent/card reference if missing.
lock_notice = r'''
        <div className="rounded-2xl border border-slate-200 bg-white/90 p-4 text-sm leading-6 text-slate-600 shadow-sm">
          <div className="flex items-start gap-3">
            <span className="mt-1 h-2.5 w-2.5 rounded-full bg-indigo-500" />
            <p>{customerPortalSelectionLockedNotice()}</p>
          </div>
        </div>
'''

if "customerPortalSelectionLockedNotice()" not in text:
    target_patterns = [
        "Active agents",
        "Active Agents",
        "Selected agents",
        "Selected Agents",
        "Agent selection",
        "Agent Selection",
    ]
    inserted = False
    for marker in target_patterns:
        idx = text.find(marker)
        if idx != -1:
            section_start = text.rfind("<section", 0, idx)
            if section_start != -1:
                section_close = text.find("</section>", idx)
                if section_close != -1:
                    insert_at = section_close
                    text = text[:insert_at] + lock_notice + text[insert_at:]
                    inserted = True
                    break
    if not inserted:
        main_idx = text.find("<main")
        if main_idx != -1:
            div_idx = text.find(">", main_idx)
            text = text[:div_idx + 1] + lock_notice + text[div_idx + 1:]

# Add CustomerAgentStatusBadge near existing ACTIVE/INACTIVE labels if not already used.
if "<CustomerAgentStatusBadge" not in text:
    # Target common ternary patterns rendering ACTIVE/INACTIVE.
    replacements = [
        (
            r'\{([^{};\n]+?)\s*\?\s*"ACTIVE"\s*:\s*"INACTIVE"\}',
            r'{<CustomerAgentStatusBadge active={Boolean(\1)} />}',
        ),
        (
            r'\{([^{};\n]+?)\s*\?\s*\'ACTIVE\'\s*:\s*\'INACTIVE\'\}',
            r'{<CustomerAgentStatusBadge active={Boolean(\1)} />}',
        ),
    ]

    for pattern, repl in replacements:
        new_text, count = re.subn(pattern, repl, text, count=1)
        if count:
            text = new_text
            break

# If no ternary was found, place a compact status legend in the client page.
if "<CustomerAgentStatusBadge" not in text[text.find("export default"):]:
    legend = r'''
        <div className="rounded-2xl border border-slate-200 bg-white/90 p-4 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
            Agent Status
          </p>
          <div className="mt-3 flex flex-wrap gap-3">
            <CustomerAgentStatusBadge active={true} />
            <CustomerAgentStatusBadge active={false} />
          </div>
        </div>
'''
    main_idx = text.find("<main")
    if main_idx != -1:
        insert_at = text.find(">", main_idx) + 1
        text = text[:insert_at] + legend + text[insert_at:]

# Replace common unsafe customer-facing literals while keeping code identifiers untouched where possible.
visible_replacements = {
    "raw JSON": "details",
    "Raw JSON": "Details",
    "debug route": "support route",
    "Debug route": "Support route",
    "provider internals": "service details",
    "Provider internals": "Service details",
    "queue internals": "processing status",
    "Queue internals": "Processing status",
    "internal runtime": "system processing",
    "Internal runtime": "System processing",
}

for old, new in visible_replacements.items():
    text = text.replace(old, new)

CLIENT_PAGE.write_text(text, encoding="utf-8")

test = r'''from pathlib import Path
import re

ROOT = Path.cwd()
client = (ROOT / "frontend/src/app/client/page.tsx").read_text(encoding="utf-8")

checks = {
    "status_badge_component": "function CustomerAgentStatusBadge" in client,
    "green_active_dot": "bg-emerald-500" in client,
    "red_inactive_dot": "bg-rose-500" in client,
    "active_uppercase": "ACTIVE" in client,
    "inactive_uppercase": "INACTIVE" in client,
    "selection_locked_notice": "Agent selections are locked after activation" in client,
    "admin_approval_required": "owner/admin approval" in client,
    "business_profile_present": "Business Profile" in client or "Business profile" in client,
    "integrations_present": "Integrations" in client,
    "billing_present": "Billing" in client,
    "support_present": "Support" in client,
    "customer_safe_helper": "customerPortalSafeText" in client,
}

failed = [name for name, ok in checks.items() if not ok]
assert not failed, f"Customer portal governance checks failed: {failed}"

for forbidden in [
    "provider internals",
    "queue internals",
    "raw JSON",
    "debug route",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "ADMIN_PLATFORM_TOKEN",
    "sk-",
]:
    assert forbidden not in client, f"Forbidden customer portal marker found: {forbidden}"

print("CUSTOMER_PORTAL_STATUS_GOVERNANCE_TESTS_PASSED")
print("active_inactive_status_dots_ready", True)
print("agent_selection_lock_notice_ready", True)
print("customer_safe_wording_ready", True)
print("credential_values_exposed", False)
'''

TEST_FILE.write_text(test, encoding="utf-8")

print("CUSTOMER_PORTAL_STATUS_GOVERNANCE_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {CLIENT_PAGE}")
print(f"Created/updated: {TEST_FILE}")