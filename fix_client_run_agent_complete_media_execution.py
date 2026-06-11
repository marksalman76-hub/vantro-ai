from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
COMPONENT = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
TEST = ROOT / "test_client_run_agent_complete_media_execution.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"client_run_agent_complete_media_execution_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [CLIENT_PAGE, COMPONENT, TEST]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

component = COMPONENT.read_text(encoding="utf-8")

if "UNIVERSAL_COMPLETE_MEDIA_SHARED_STATE_V1" not in component:
    component = component.replace(
        "type UniversalCompleteMediaRunAgentPanelProps = {\n  selectedAgent?: string;\n  businessProfile?: Record<string, string>;\n  onResult?: (deliverable: Record<string, unknown>) => void;\n};",
        """type UniversalCompleteMediaRunAgentPanelProps = {
  selectedAgent?: string;
  businessProfile?: Record<string, string>;
  onResult?: (deliverable: Record<string, unknown>) => void;
  onConfigChange?: (config: Record<string, unknown>) => void;
};""",
        1,
    )

    component = component.replace(
        "  onResult,\n}: UniversalCompleteMediaRunAgentPanelProps) {",
        """  onResult,
  onConfigChange,
}: UniversalCompleteMediaRunAgentPanelProps) {""",
        1,
    )

    component = component.replace(
        "  const previewUrl = result?.preview_url || result?.signed_preview_url || clientSafeAssetUrl(result);",
        """  const previewUrl = result?.preview_url || result?.signed_preview_url || clientSafeAssetUrl(result);

  // UNIVERSAL_COMPLETE_MEDIA_SHARED_STATE_V1
  useEffect(() => {
    onConfigChange?.({
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
    });
  }, [
    enabled,
    prompt,
    outputType,
    platform,
    durationSeconds,
    aspectRatio,
    language,
    accent,
    tone,
    voiceStyle,
    ageRange,
    genderPresentation,
    ethnicityAppearance,
    avatarLikeness,
    facialFeatures,
    expressions,
    gestures,
    wardrobe,
    backgroundSetting,
    visualStyle,
    cameraMovement,
    musicStyle,
    soundEffects,
    callToAction,
    onConfigChange,
  ]);""",
        1,
    )

COMPONENT.write_text(component, encoding="utf-8")

client = CLIENT_PAGE.read_text(encoding="utf-8")

if "const [universalCompleteMediaConfig" not in client:
    client = client.replace(
        '  const [showMediaPreviewOverlay, setShowMediaPreviewOverlay] = useState(false);\n  const [selectedAssetIndex, setSelectedAssetIndex] = useState(0);',
        '''  const [showMediaPreviewOverlay, setShowMediaPreviewOverlay] = useState(false);
  const [selectedAssetIndex, setSelectedAssetIndex] = useState(0);
  const [universalCompleteMediaConfig, setUniversalCompleteMediaConfig] = useState<Record<string, unknown>>({});''',
        1,
    )

client = client.replace(
    '              onResult={(deliverable) => {',
    '''              onConfigChange={setUniversalCompleteMediaConfig}
              onResult={(deliverable) => {''',
    1,
)

if "CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_V1" not in client:
    old = '''                    setExecutionState("running");
                    setToastMessage("Execution started. Generating client deliverables...");

                    try {
                      const response = await fetch("/api/delegated-workforce-execution", {'''

    new = '''                    setExecutionState("running");
                    setToastMessage("Execution started. Generating client deliverables...");

                    // CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_V1
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
                      });

                      const data = await response.json();

                      if (!response.ok || !data?.success) {
                        throw new Error(data?.reason || data?.message || data?.error || "Complete media execution failed");
                      }

                      const jobId = data?.job_id;
                      const deliverable = {
                        title: "Complete media file",
                        summary: data?.message || "Complete media workflow accepted. The final synced file is being generated.",
                        output: data?.message || "Complete media workflow accepted.",
                        generated_output: data?.message || "Complete media workflow accepted.",
                        content: data?.message || "Complete media workflow accepted.",
                        preview_url: data?.preview_url || "",
                        asset_url: data?.asset_url || "",
                        download_url: data?.download_url || "",
                        media_url: data?.preview_url || data?.asset_url || "",
                        generation_jobs: jobId ? [{ job_id: jobId, status: data?.status || "queued", type: "universal_complete_media" }] : [],
                        tags: ["Complete media", "Client safe", "Generated output"],
                        created_at: new Date().toISOString(),
                      };

                      setLiveDeliverable(deliverable as any);
                      setSelectedAssetIndex(0);
                      setExecutionState("completed");
                      setToastMessage(jobId ? `Complete media workflow queued. Job: ${jobId}` : "Complete media workflow queued.");
                      return;
                    }

                    try {
                      const response = await fetch("/api/delegated-workforce-execution", {'''

    if old not in client:
        raise SystemExit("RUN_AGENT_EXECUTION_BLOCK_NOT_FOUND")

    client = client.replace(old, new, 1)

CLIENT_PAGE.write_text(client, encoding="utf-8")

TEST.write_text(
    r'''from pathlib import Path


def test_run_agent_complete_media_execution_wired():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_V1" in client, "Run Agent complete media execution marker missing"
    assert "universalCompleteMediaConfig" in client, "shared complete media config state missing"
    assert 'fetch("/api/universal-complete-media"' in client, "Run Agent does not call complete media route"
    assert 'fetch("/api/delegated-workforce-execution"' in client, "normal delegated route must remain as fallback"
    assert "UNIVERSAL_COMPLETE_MEDIA_SHARED_STATE_V1" in component, "component shared state marker missing"
    assert "onConfigChange" in component, "component must expose config changes"


if __name__ == "__main__":
    test_run_agent_complete_media_execution_wired()
    print("CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_TEST_PASSED")
''',
    encoding="utf-8",
)

print("CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_FIXED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {CLIENT_PAGE}")
print(f"Updated: {COMPONENT}")
print(f"Created: {TEST}")