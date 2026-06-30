import {
  CREATIVE_AGENT_OPTIONS,
  BRIEF_STEP_FIELD_ORDER,
  getCreativeAgentBoundaryLabel,
  isCreativeAgentOptionAllowed,
  resolveCreateMediaAgentId,
  type MediaRequest,
} from "../page";

describe("admin create media agent selection", () => {
  const request: MediaRequest = {
    type: "social_ad",
    brief: "Create a launch ad",
    platform: "Instagram",
    aspect_ratio: "9:16 (vertical)",
    tone: "Professional",
    age_range: "",
    gender: "",
    ethnicity: "",
    language: "English",
    video_quality: "4K",
    use_brand_profile: true,
  };

  it("uses the explicitly selected creative agent instead of auto-assigning", () => {
    expect(resolveCreateMediaAgentId(request, "ad_creative_agent")).toBe("ad_creative_agent");
  });

  it("exposes all creative agents that can be selected from the brief step", () => {
    expect(CREATIVE_AGENT_OPTIONS.map((agent) => agent.id)).toEqual([
      "ugc_media_agent",
      "ugc_creative_agent",
      "product_image_agent",
      "ad_creative_agent",
      "creative_rotation_agent",
      "social_media_content_agent",
      "ads_optimisation_agent",
    ]);
  });

  it("keeps creative agent selection as the first control in the brief step", () => {
    expect(BRIEF_STEP_FIELD_ORDER).toEqual([
      "creative_agent",
      "brief_text",
      "reference_files",
    ]);
  });

  it("blocks a selected creative agent when the request exceeds its media model boundary", () => {
    expect(isCreativeAgentOptionAllowed("ad_creative_agent", request)).toEqual({
      allowed: false,
      reason: "Video model boundary: supports 720p and 1080p only.",
    });
  });

  it("blocks image-only creative agents from video requests", () => {
    expect(isCreativeAgentOptionAllowed("product_image_agent", request)).toEqual({
      allowed: false,
      reason: "Media boundary: image assets only.",
    });
  });

  it("describes each creative agent boundary in the selector", () => {
    expect(getCreativeAgentBoundaryLabel("ugc_creative_agent")).toBe("Video: 720p, 1080p, 4K. Image: standard, pro.");
    expect(getCreativeAgentBoundaryLabel("creative_rotation_agent")).toBe("Video: 720p only. Image: standard.");
  });

  it("renders the brief step agent selector as a labeled dropdown before the brief text", () => {
    const source = require("node:fs").readFileSync(__dirname + "/../page.tsx", "utf8");
    const selectorIndex = source.indexOf('id="creative-agent-selector"');
    const labelIndex = source.indexOf('htmlFor="creative-agent-selector"');
    const textareaIndex = source.indexOf("data-brief-field={BRIEF_STEP_FIELD_ORDER[1]}");

    expect(labelIndex).toBeGreaterThan(-1);
    expect(selectorIndex).toBeGreaterThan(labelIndex);
    expect(selectorIndex).toBeLessThan(textareaIndex);
  });
});
