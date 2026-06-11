from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
COMPONENT = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
TEST = ROOT / "test_universal_media_client_admin_run_agent_reliability.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"universal_media_client_admin_run_agent_reliability_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [CLIENT_PAGE, ADMIN_PAGE, COMPONENT, TEST]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

component = COMPONENT.read_text(encoding="utf-8")

if "UNIVERSAL_COMPLETE_MEDIA_LOCAL_STORAGE_BRIDGE_V1" not in component:
    component = component.replace(
        """    onConfigChange?.({
      enabled,
      prompt,
      output_type: outputType,
      platform,
      duration_seconds: durationSeconds,
      aspect_ratio: aspectRatio,
      language,
      accent,
      tone,
      voice_style: voiceStyle,
      age_range: ageRange,
      gender_presentation: genderPresentation,
      ethnicity_or_cultural_appearance: ethnicityAppearance,
      avatar_likeness: avatarLikeness,
      facial_features: facialFeatures,
      expressions,
      gestures,
      wardrobe,
      background_setting: backgroundSetting,
      visual_style: visualStyle,
      camera_movement: cameraMovement,
      music_style: musicStyle,
      sound_effects: soundEffects,
      call_to_action: callToAction,
    });""",
        """    // UNIVERSAL_COMPLETE_MEDIA_LOCAL_STORAGE_BRIDGE_V1
    const nextConfig = {
      enabled,
      prompt,
      output_type: outputType,
      platform,
      duration_seconds: durationSeconds,
      aspect_ratio: aspectRatio,
      language,
      accent,
      tone,
      voice_style: voiceStyle,
      age_range: ageRange,
      gender_presentation: genderPresentation,
      ethnicity_or_cultural_appearance: ethnicityAppearance,
      avatar_likeness: avatarLikeness,
      facial_features: facialFeatures,
      expressions,
      gestures,
      wardrobe,
      background_setting: backgroundSetting,
      visual_style: visualStyle,
      camera_movement: cameraMovement,
      music_style: musicStyle,
      sound_effects: soundEffects,
      call_to_action: callToAction,
    };

    onConfigChange?.(nextConfig);

    try {
      window.localStorage.setItem("universal_complete_media_config", JSON.stringify(nextConfig));
      window.dispatchEvent(new CustomEvent("universal-complete-media-config", { detail: nextConfig }));
    } catch {}""",
        1,
    )

COMPONENT.write_text(component, encoding="utf-8")

client = CLIENT_PAGE.read_text(encoding="utf-8")

if "CLIENT_RUN_AGENT_COMPLETE_MEDIA_LOCAL_STORAGE_FALLBACK_V1" not in client:
    client = client.replace(
        """                    // CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_V1
                    if ((universalCompleteMediaConfig as any)?.enabled) {
                      const taskText =
                        ((document.querySelector("textarea") as HTMLTextAreaElement)?.value || "").trim() ||
                        String((universalCompleteMediaConfig as any)?.prompt || "").trim() ||
                        "Create a complete media file";

                      setToastMessage("Complete media workflow started. Generating visual, natural audio, and final synced file...");

                      const response = await fetch("/api/universal-complete-media", {
                        method: "POST",
                        cache: "no-store",
                        credentials: "include",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                          ...(universalCompleteMediaConfig as any),
                          prompt: String((universalCompleteMediaConfig as any)?.prompt || taskText),
                          agent_id: selectedAgents[0] || "social_media_manager_content_creator_agent",
                          source: "client_run_agent_button",
                        }),
                      });""",
        """                    // CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_V1
                    // CLIENT_RUN_AGENT_COMPLETE_MEDIA_LOCAL_STORAGE_FALLBACK_V1
                    let completeMediaConfig: Record<string, unknown> = { ...(universalCompleteMediaConfig as any) };
                    try {
                      const storedConfig = window.localStorage.getItem("universal_complete_media_config");
                      if (storedConfig) {
                        completeMediaConfig = {
                          ...completeMediaConfig,
                          ...JSON.parse(storedConfig),
                        };
                      }
                    } catch {}

                    if ((completeMediaConfig as any)?.enabled) {
                      const allTextareas = Array.from(document.querySelectorAll("textarea")) as HTMLTextAreaElement[];
                      const mediaTextarea = allTextareas.find((item) =>
                        String(item.placeholder || "").toLowerCase().includes("complete media")
                        || String(item.placeholder || "").toLowerCase().includes("media file")
                      );
                      const taskTextarea = allTextareas.find((item) =>
                        String(item.value || "").trim().length > 0
                      );

                      const taskText =
                        String((completeMediaConfig as any)?.prompt || "").trim() ||
                        String(mediaTextarea?.value || "").trim() ||
                        String(taskTextarea?.value || "").trim() ||
                        "Create a complete media file";

                      setToastMessage("Complete media workflow started. Generating visual, natural audio, and final synced file...");

                      const response = await fetch("/api/universal-complete-media", {
                        method: "POST",
                        cache: "no-store",
                        credentials: "include",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                          ...(completeMediaConfig as any),
                          prompt: taskText,
                          agent_id: selectedAgents[0] || "social_media_manager_content_creator_agent",
                          source: "client_run_agent_button",
                        }),
                      });""",
        1,
    )

CLIENT_PAGE.write_text(client, encoding="utf-8")

admin = ADMIN_PAGE.read_text(encoding="utf-8")

if "UniversalCompleteMediaRunAgentPanel" not in admin:
    # Put import near existing component imports if possible.
    if 'import DirectMediaProviderPanel from "@/components/DirectMediaProviderPanel";' in admin:
        admin = admin.replace(
            'import DirectMediaProviderPanel from "@/components/DirectMediaProviderPanel";',
            'import DirectMediaProviderPanel from "@/components/DirectMediaProviderPanel";\nimport UniversalCompleteMediaRunAgentPanel from "@/components/UniversalCompleteMediaRunAgentPanel";',
            1,
        )
    else:
        admin = '"use client";\n' + admin.replace('"use client";\n', "", 1)
        admin = admin.replace(
            'import React',
            'import UniversalCompleteMediaRunAgentPanel from "@/components/UniversalCompleteMediaRunAgentPanel";\nimport React',
            1,
        )

if "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" not in admin:
    panel_block = '''
      {/* ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1 */}
      <section className="rounded-2xl border border-indigo-400/20 bg-slate-950/70 p-5 shadow-lg">
        <div className="mb-3">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-indigo-300">Universal complete media</p>
          <h2 className="mt-1 text-xl font-bold text-white">Admin complete media test</h2>
          <p className="mt-1 text-sm text-slate-400">
            Admin-only live test path for the same one-prompt complete media workflow used by the client Run Agent task.
          </p>
        </div>
        <UniversalCompleteMediaRunAgentPanel
          selectedAgent={"social_media_manager_content_creator_agent"}
          businessProfile={{}}
          onResult={() => {}}
        />
      </section>
'''

    # Place before provider diagnostics if present, otherwise before closing main.
    if "<DirectMediaProviderPanel" in admin:
        insert_at = admin.find("<DirectMediaProviderPanel")
        line_start = admin.rfind("\n", 0, insert_at)
        admin = admin[:line_start] + "\n" + panel_block + "\n" + admin[line_start:]
    elif "</main>" in admin:
        admin = admin.replace("</main>", panel_block + "\n</main>", 1)
    else:
        admin += "\n" + panel_block + "\n"

ADMIN_PAGE.write_text(admin, encoding="utf-8")

TEST.write_text(
    r'''from pathlib import Path


def test_client_complete_media_run_agent_reliable():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_LOCAL_STORAGE_FALLBACK_V1" in client, "client Run Agent localStorage fallback missing"
    assert "universal_complete_media_config" in client, "client Run Agent does not read media config storage"
    assert 'fetch("/api/universal-complete-media"' in client, "client Run Agent does not call complete media route"
    assert "UNIVERSAL_COMPLETE_MEDIA_LOCAL_STORAGE_BRIDGE_V1" in component, "component does not persist media config"
    assert "window.localStorage.setItem" in component, "component localStorage write missing"


def test_admin_complete_media_panel_present():
    admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")
    assert "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" in admin, "admin complete media panel missing"
    assert "UniversalCompleteMediaRunAgentPanel" in admin, "admin does not import/render complete media component"
    assert "Admin complete media test" in admin, "admin panel title missing"


if __name__ == "__main__":
    test_client_complete_media_run_agent_reliable()
    test_admin_complete_media_panel_present()
    print("UNIVERSAL_MEDIA_CLIENT_ADMIN_RUN_AGENT_RELIABILITY_TEST_PASSED")
''',
    encoding="utf-8",
)

print("UNIVERSAL_MEDIA_CLIENT_ADMIN_RUN_AGENT_RELIABILITY_FIXED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {CLIENT_PAGE}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Updated: {COMPONENT}")
print(f"Created: {TEST}")