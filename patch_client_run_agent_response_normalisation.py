from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''                    if (data?.success) {
                      setLiveDeliverable(data.deliverable);
                      setSelectedAssetIndex(0);
                      setExecutionState("completed");
                      setReviewStatus("pending");
                      setToastMessage("Client deliverable generated and ready for review.");
                    } else {
'''

new = '''                    if (data?.success) {
                      const firstResult = Array.isArray(data?.completed_results) ? data.completed_results[0] : null;
                      const deliverable = data?.deliverable || firstResult?.deliverable || firstResult || data;

                      const richDeliverable = {
                        ...deliverable,
                        title: deliverable?.title || firstResult?.deliverable?.title || "Client deliverable",
                        summary: deliverable?.summary || firstResult?.deliverable?.summary || firstResult?.completed_output || data?.summary || "",
                        output: deliverable?.output || firstResult?.completed_output || firstResult?.deliverable?.content?.body || data?.output || "",
                        preview_url: deliverable?.preview_url || firstResult?.preview_url || firstResult?.deliverable?.preview_url || "",
                        asset_url: deliverable?.asset_url || firstResult?.asset_url || firstResult?.deliverable?.asset_url || "",
                        media_url: deliverable?.media_url || firstResult?.media_url || firstResult?.deliverable?.media_url || "",
                        generated_files: deliverable?.generated_files || firstResult?.generated_files || firstResult?.deliverable?.generated_files || [],
                        media_pack: deliverable?.media_pack || firstResult?.media_pack || firstResult?.deliverable?.media_pack || {},
                        generation_jobs: deliverable?.generation_jobs || firstResult?.generation_jobs || firstResult?.deliverable?.generation_jobs || [],
                        voiceover_script: deliverable?.voiceover_script || firstResult?.voiceover_script || "",
                        video_prompt: deliverable?.video_prompt || firstResult?.video_prompt || "",
                        avatar_prompt: deliverable?.avatar_prompt || firstResult?.avatar_prompt || "",
                        supports_audio: deliverable?.supports_audio ?? firstResult?.supports_audio ?? false,
                        supports_video: deliverable?.supports_video ?? firstResult?.supports_video ?? false,
                        supports_avatar_video: deliverable?.supports_avatar_video ?? firstResult?.supports_avatar_video ?? false,
                        client_safe_learning_summary: deliverable?.client_safe_learning_summary || firstResult?.client_safe_learning_summary || {},
                        proprietary_logic_hidden: true,
                        created_at: deliverable?.created_at || firstResult?.created_at || new Date().toISOString(),
                      };

                      setLiveDeliverable(richDeliverable);
                      setSelectedAssetIndex(0);
                      setExecutionState("completed");
                      setReviewStatus("pending");
                      setToastMessage("Client deliverable generated and ready for review.");
                    } else {
'''

if old not in text:
    raise SystemExit("client run-agent success block not found")

text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("CLIENT_RUN_AGENT_RESPONSE_NORMALISATION_PATCHED")