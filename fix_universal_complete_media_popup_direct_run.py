from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"complete_media_popup_direct_run_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

if "Create complete media now" in text:
    print("DIRECT_RUN_BUTTON_ALREADY_PRESENT")
else:
    old_header = "Configure optional media output here. The actual execution still happens through the main Run Agent button."
    new_header = "Configure optional media output here, then click Create complete media now to run directly from this popup."

    if old_header in text:
        text = text.replace(old_header, new_header)
    else:
        print("WARNING_HEADER_TEXT_NOT_FOUND")

    marker = '"Show advanced media controls"'
    marker_index = text.find(marker)
    if marker_index == -1:
        raise SystemExit("SHOW_ADVANCED_MEDIA_CONTROLS_MARKER_NOT_FOUND")

    close_button_index = text.find("</button>", marker_index)
    if close_button_index == -1:
        raise SystemExit("ADVANCED_CONTROLS_BUTTON_CLOSE_NOT_FOUND")

    insert_at = close_button_index + len("</button>")

    direct_run_button = r'''
              <button
                type="button"
                data-complete-media-run-now="true"
                onClick={() => {
                  try {
                    const rawConfig = window.localStorage.getItem("universal_complete_media_config");
                    const config = rawConfig ? JSON.parse(rawConfig) : {};
                    const nextConfig = {
                      ...config,
                      enabled: true,
                      run_direct_from_popup: true,
                      requested_from: "complete_media_popup",
                    };

                    window.localStorage.setItem("universal_complete_media_config", JSON.stringify(nextConfig));
                    window.dispatchEvent(
                      new CustomEvent("universal-complete-media-config", {
                        detail: nextConfig,
                      })
                    );

                    const buttons = Array.from(document.querySelectorAll("button"));
                    const runAgentButton = buttons.find((button) => {
                      const label = (button.textContent || "").replace(/\s+/g, " ").trim();
                      return label === "Run Agent";
                    });

                    if (runAgentButton instanceof HTMLButtonElement) {
                      runAgentButton.click();
                    } else {
                      window.dispatchEvent(
                        new CustomEvent("universal-complete-media-run-now", {
                          detail: nextConfig,
                        })
                      );
                    }
                  } catch {
                    window.dispatchEvent(
                      new CustomEvent("universal-complete-media-run-now", {
                        detail: {
                          enabled: true,
                          run_direct_from_popup: true,
                          requested_from: "complete_media_popup",
                        },
                      })
                    );
                  }
                }}
                style={{
                  width: "fit-content",
                  border: "1px solid rgba(34,197,94,.36)",
                  borderRadius: 999,
                  padding: "10px 14px",
                  background:
                    mode === "admin"
                      ? "linear-gradient(135deg, rgba(34,197,94,.24), rgba(6,182,212,.16))"
                      : "linear-gradient(135deg, rgba(34,197,94,.12), rgba(79,70,229,.10))",
                  color: mode === "admin" ? "#bbf7d0" : "#166534",
                  fontWeight: 950,
                  cursor: "pointer",
                  boxShadow: "0 14px 34px rgba(15,23,42,.18)",
                }}
              >
                Create complete media now
              </button>'''

    text = text[:insert_at] + direct_run_button + text[insert_at:]

    old_footer_a = "Saved. Close this popup and click the main "
    new_footer_a = "Saved. Click "
    if old_footer_a in text:
        text = text.replace(old_footer_a, new_footer_a)

    old_footer_b = " button to execute with these media settings."
    new_footer_b = " to execute with these media settings, or close this popup without running."
    if old_footer_b in text:
        text = text.replace(old_footer_b, new_footer_b)

    TARGET.write_text(text, encoding="utf-8")
    print("DIRECT_COMPLETE_MEDIA_POPUP_RUN_BUTTON_INSTALLED")

verify_text = TARGET.read_text(encoding="utf-8")
required = [
    "Create complete media now",
    "data-complete-media-run-now",
    "universal-complete-media-run-now",
    "run_direct_from_popup",
]

missing = [item for item in required if item not in verify_text]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")
print("DIRECT_COMPLETE_MEDIA_POPUP_RUN_BUTTON_VERIFIED")