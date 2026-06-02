from pathlib import Path

files = [
    Path("frontend/src/app/admin/live-execution/page.tsx"),
    Path("frontend/src/app/client/page.tsx"),
]

for p in files:
    text = p.read_text(encoding="utf-8")

    marker = "media_pack"
    if marker not in text:
        text = text.replace(
            "generation_jobs",
            "generation_jobs, media_pack, voiceover_script, video_prompt, avatar_prompt, supports_audio, supports_video, supports_avatar_video, client_safe_learning_summary",
        )

    # Add a compact client-safe media pack text fallback wherever latest output summary is rendered.
    insert = '''
function renderMediaPackSummary(result: any) {
  const mediaPack = result?.media_pack || result?.deliverable?.media_pack || {};
  const jobs = result?.generation_jobs || mediaPack?.generation_jobs || [];
  const voiceover = result?.voiceover_script || mediaPack?.voiceover_script || "";
  const videoPrompt = result?.video_prompt || mediaPack?.video_prompt || "";
  const avatarPrompt = result?.avatar_prompt || mediaPack?.avatar_prompt || "";
  const learning = result?.client_safe_learning_summary || {};

  if (!jobs.length && !voiceover && !videoPrompt && !avatarPrompt) return "";

  return [
    "Creative media pack ready",
    result?.supports_audio ? "Audio: voiceover-ready" : "",
    result?.supports_video ? "Video: prompt/job-ready" : "",
    result?.supports_avatar_video ? "Avatar: presenter-ready" : "",
    jobs.length ? `Generation jobs: ${jobs.length}` : "",
    learning?.message ? `Learning: ${learning.message}` : "",
    voiceover ? `Voiceover script: ${voiceover.slice(0, 240)}...` : "",
    videoPrompt ? `Video prompt: ${videoPrompt.slice(0, 240)}...` : "",
    avatarPrompt ? `Avatar prompt: ${avatarPrompt.slice(0, 240)}...` : "",
  ].filter(Boolean).join("\\n\\n");
}
'''

    if "function renderMediaPackSummary" not in text:
        # place after imports / use client area safely
        if '"use client";' in text:
            text = text.replace('"use client";', '"use client";\n' + insert, 1)
        else:
            text = insert + "\n" + text

    p.write_text(text, encoding="utf-8")
    print("PATCHED", p)