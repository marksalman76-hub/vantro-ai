from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old_assets = '''  const attachedAssets = [
    ...directMediaAssets,
    ...(liveDeliverable?.assets || []),
    ...(liveDeliverable?.images || []),
  ].filter((asset, index, list) => {
'''

new_assets = '''  const mediaPackAny = (liveDeliverable as any)?.media_pack || {};
  const mediaPackImageAssets = Array.isArray(mediaPackAny?.image_assets) ? mediaPackAny.image_assets : [];
  const mediaPackGeneratedJobs = Array.isArray((liveDeliverable as any)?.generation_jobs)
    ? (liveDeliverable as any).generation_jobs
    : Array.isArray(mediaPackAny?.generation_jobs)
      ? mediaPackAny.generation_jobs
      : [];

  const mediaPackAssets = mediaPackImageAssets
    .map((asset: any) => ({
      url: asset?.preview_url || asset?.asset_url || asset?.media_url || "",
      image_url: asset?.preview_url || asset?.asset_url || asset?.media_url || "",
      title: "Generated creative media asset",
      name: "Generated creative media asset",
      type: asset?.generation_type || "image",
      source: asset?.provider || "creative_media_pack",
    }))
    .filter((asset: any) => asset.url || asset.image_url);

  const attachedAssets = [
    ...directMediaAssets,
    ...mediaPackAssets,
    ...(liveDeliverable?.assets || []),
    ...(liveDeliverable?.images || []),
  ].filter((asset, index, list) => {
'''

if old_assets not in text:
    raise SystemExit("attachedAssets block not found")

text = text.replace(old_assets, new_assets, 1)

old_outcome = '''  const visibleClientOutcomeText =
    liveDeliverableAny?.output ||
    liveDeliverableAny?.generated_output ||
    liveDeliverableAny?.provider_output ||
    liveDeliverableAny?.content ||
    liveDeliverableAny?.summary ||
    liveDeliverableAny?.message ||
    "";
'''

new_outcome = '''  const mediaPackSummaryText = [
    liveDeliverableAny?.supports_audio ? "Audio: voiceover-ready" : "",
    liveDeliverableAny?.supports_video ? "Video: prompt/job-ready" : "",
    liveDeliverableAny?.supports_avatar_video ? "Avatar: presenter-ready" : "",
    mediaPackGeneratedJobs.length ? `Generation jobs: ${mediaPackGeneratedJobs.length}` : "",
    liveDeliverableAny?.client_safe_learning_summary?.message ? `Learning: ${liveDeliverableAny.client_safe_learning_summary.message}` : "",
    liveDeliverableAny?.voiceover_script ? `Voiceover script:\\n${String(liveDeliverableAny.voiceover_script).slice(0, 700)}` : "",
    liveDeliverableAny?.video_prompt ? `Video prompt:\\n${String(liveDeliverableAny.video_prompt).slice(0, 700)}` : "",
    liveDeliverableAny?.avatar_prompt ? `Avatar prompt:\\n${String(liveDeliverableAny.avatar_prompt).slice(0, 700)}` : "",
  ].filter(Boolean).join("\\n\\n");

  const visibleClientOutcomeText =
    mediaPackSummaryText ||
    liveDeliverableAny?.output ||
    liveDeliverableAny?.generated_output ||
    liveDeliverableAny?.provider_output ||
    liveDeliverableAny?.content ||
    liveDeliverableAny?.summary ||
    liveDeliverableAny?.message ||
    "";
'''

if old_outcome not in text:
    raise SystemExit("visibleClientOutcomeText block not found")

text = text.replace(old_outcome, new_outcome, 1)

old_pending = '''                          Pending media
'''

new_pending = '''                          {attachedAssets.length ? "Assets detected" : "Pending media"}
'''

text = text.replace(old_pending, new_pending, 1)

p.write_text(text, encoding="utf-8")
print("CLIENT_MEDIA_PACK_BINDING_PATCHED")