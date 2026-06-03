export type AgentOutputContract = {
  agent_key: string;
  display_name: string;
  category: string;
  deliverable_type: string;
  required_sections: string[];
  client_safe: true;
  owner_approval_required_for_external_action: boolean;
  supports_media_assets: boolean;
  supports_execution_actions: boolean;
  minimum_quality_standard: string;
};

export type ContractValidationResult = {
  success: boolean;
  all_agent_output_contracts_enabled: true;
  agent_key: string;
  contract_found: boolean;
  contract: AgentOutputContract;
  missing_sections: string[];
  quality_passed: boolean;
  client_safe: boolean;
  output_contract_status: "passed" | "needs_revision";
  output_contract_reason: string;
};

const DEFAULT_REQUIRED_SECTIONS = [
  "Executive summary",
  "Recommended actions",
  "Client-ready deliverable",
  "Next step",
];

export const ALL_AGENT_OUTPUT_CONTRACTS: AgentOutputContract[] = [
  {
    agent_key: "head_agent",
    display_name: "Head Agent",
    category: "Enterprise Control",
    deliverable_type: "executive_orchestration_summary",
    required_sections: ["Executive summary", "Cross-agent findings", "Recommendations", "Owner decision required"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: false,
    minimum_quality_standard: "Enterprise-level governance summary with owner-only decisions preserved.",
  },
  {
    agent_key: "strategist_agent",
    display_name: "Strategist Agent",
    category: "Strategy",
    deliverable_type: "business_strategy_plan",
    required_sections: ["Strategic diagnosis", "Commercial opportunity", "Recommended actions", "Risks"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "Actionable, commercially specific strategy guidance.",
  },
  {
    agent_key: "business_growth_partnerships_agent",
    display_name: "Business Growth & Partnerships Agent",
    category: "Growth",
    deliverable_type: "growth_partnership_plan",
    required_sections: ["Growth opportunity", "Partnership targets", "Outreach plan", "Next step"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "Specific growth opportunities with partner-fit reasoning.",
  },
  {
    agent_key: "lead_generator_appointment_setter_agent",
    display_name: "Lead Generator / Appointment Setter Agent",
    category: "Sales",
    deliverable_type: "lead_generation_plan",
    required_sections: ["Target lead profile", "Lead source plan", "Outreach sequence", "Qualification criteria"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "Qualified, targeted outreach plan with clear appointment objective.",
  },
  {
    agent_key: "marketing_specialist_agent",
    display_name: "Marketing Specialist Agent",
    category: "Marketing",
    deliverable_type: "marketing_campaign_deliverable",
    required_sections: ["Campaign objective", "Target audience", "Messaging angle", "Execution plan"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Premium, conversion-focused campaign output.",
  },
  {
    agent_key: "social_media_manager_content_creator_agent",
    display_name: "Social Media Manager / Content Creator Agent",
    category: "Marketing",
    deliverable_type: "social_content_pack",
    required_sections: ["Content pillars", "Post ideas", "Captions", "Publishing recommendations"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Platform-aware content suitable for real posting.",
  },
  {
    agent_key: "seo_agent",
    display_name: "SEO Agent",
    category: "SEO",
    deliverable_type: "seo_optimisation_report",
    required_sections: ["SEO diagnosis", "Keyword opportunities", "On-page recommendations", "Priority fixes"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "White-hat SEO recommendations with business relevance.",
  },
  {
    agent_key: "email_reply_agent",
    display_name: "Email Reply Agent",
    category: "Communication",
    deliverable_type: "email_response_pack",
    required_sections: ["Context summary", "Recommended reply", "Tone notes", "Follow-up action"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "Professional, context-aware client-ready communication.",
  },
  {
    agent_key: "crm_ai_agent",
    display_name: "CRM AI Agent",
    category: "CRM",
    deliverable_type: "crm_action_plan",
    required_sections: ["Customer context", "Pipeline action", "Recommended follow-up", "Data hygiene notes"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "CRM-safe action recommendations with clear pipeline value.",
  },
  {
    agent_key: "sales_closer_agent",
    display_name: "Sales / Closer Agent",
    category: "Sales",
    deliverable_type: "sales_closing_plan",
    required_sections: ["Deal context", "Objections", "Close strategy", "Next follow-up"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "Commercially useful closing support with owner approval preserved.",
  },
  {
    agent_key: "receptionist_agent",
    display_name: "Receptionist Agent",
    category: "Operations",
    deliverable_type: "front_desk_response",
    required_sections: ["Caller/request summary", "Response", "Routing decision", "Next action"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "Clear, polite, operationally useful front-desk handling.",
  },
  {
    agent_key: "customer_support_agent",
    display_name: "Customer Support Agent",
    category: "Support",
    deliverable_type: "support_resolution",
    required_sections: ["Issue summary", "Resolution steps", "Customer message", "Escalation criteria"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "Helpful, safe support response with escalation boundaries.",
  },
  {
    agent_key: "ecommerce_agent",
    display_name: "Ecommerce Agent",
    category: "Ecommerce",
    deliverable_type: "ecommerce_growth_action",
    required_sections: ["Store diagnosis", "Conversion opportunity", "Recommended changes", "Expected impact"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Conversion-focused ecommerce recommendations.",
  },
  {
    agent_key: "product_research_agent",
    display_name: "Product Research Agent",
    category: "Product",
    deliverable_type: "product_research_report",
    required_sections: ["Product opportunity", "Market evidence", "Customer fit", "Recommendation"],
    client_safe: true,
    owner_approval_required_for_external_action: false,
    supports_media_assets: false,
    supports_execution_actions: false,
    minimum_quality_standard: "Evidence-led product research with clear commercial fit.",
  },
  {
    agent_key: "competitor_intelligence_agent",
    display_name: "Competitor Intelligence Agent",
    category: "Research",
    deliverable_type: "competitor_intelligence_brief",
    required_sections: ["Competitor overview", "Positioning gaps", "Opportunity", "Recommended response"],
    client_safe: true,
    owner_approval_required_for_external_action: false,
    supports_media_assets: false,
    supports_execution_actions: false,
    minimum_quality_standard: "Balanced competitor analysis without copying competitors.",
  },
  {
    agent_key: "brand_strategy_agent",
    display_name: "Brand Strategy Agent",
    category: "Brand",
    deliverable_type: "brand_strategy_deliverable",
    required_sections: ["Brand position", "Audience insight", "Messaging direction", "Brand actions"],
    client_safe: true,
    owner_approval_required_for_external_action: false,
    supports_media_assets: true,
    supports_execution_actions: false,
    minimum_quality_standard: "Distinct, premium brand guidance.",
  },
  {
    agent_key: "store_builder_agent",
    display_name: "Store Builder Agent",
    category: "Build",
    deliverable_type: "store_build_plan",
    required_sections: ["Store structure", "Page requirements", "Conversion elements", "Launch checklist"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Build-ready ecommerce store plan.",
  },
  {
    agent_key: "website_landing_page_apps_agent",
    display_name: "Website / Landing Page / Apps Agent",
    category: "Build",
    deliverable_type: "website_app_deliverable",
    required_sections: ["Build objective", "Page/app structure", "User journey", "Implementation notes"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Build-ready website/app output with clear UX logic.",
  },
  {
    agent_key: "product_development_agent",
    display_name: "Product Development Agent",
    category: "Product",
    deliverable_type: "product_development_plan",
    required_sections: ["Product concept", "Feature priorities", "Validation plan", "Next build step"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Commercially viable product development guidance.",
  },
  {
    agent_key: "product_copywriting_agent",
    display_name: "Product Copywriting Agent",
    category: "Copywriting",
    deliverable_type: "product_copy_pack",
    required_sections: ["Product positioning", "Product title", "Description", "Conversion bullets"],
    client_safe: true,
    owner_approval_required_for_external_action: false,
    supports_media_assets: false,
    supports_execution_actions: false,
    minimum_quality_standard: "Conversion-focused product copy.",
  },
  {
    agent_key: "ugc_creative_agent",
    display_name: "UGC Creative Agent",
    category: "Creative",
    deliverable_type: "ugc_script_pack",
    required_sections: ["Hook", "Script", "Shot direction", "Call to action"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Commercially believable UGC creative suitable for paid ads.",
  },
  {
    agent_key: "product_image_agent",
    display_name: "Product Image Agent",
    category: "Creative",
    deliverable_type: "product_image_direction",
    required_sections: ["Image objective", "Scene direction", "Composition", "Usage notes"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Ad-ready image direction with realistic production detail.",
  },
  {
    agent_key: "paid_ads_agent",
    display_name: "Paid Ads Agent",
    category: "Advertising",
    deliverable_type: "paid_ads_campaign_plan",
    required_sections: ["Campaign objective", "Audience", "Ad creative", "Budget/control note"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Performance-oriented ad plan with spend approval preserved.",
  },
  {
    agent_key: "analytics_optimisation_agent",
    display_name: "Analytics Optimisation Agent",
    category: "Analytics",
    deliverable_type: "analytics_optimisation_report",
    required_sections: ["Data summary", "Performance insight", "Optimisation recommendation", "Measurement plan"],
    client_safe: true,
    owner_approval_required_for_external_action: false,
    supports_media_assets: false,
    supports_execution_actions: false,
    minimum_quality_standard: "Actionable analytics insight with measurable next steps.",
  },
  {
    agent_key: "influencer_collaboration_agent",
    display_name: "Influencer Collaboration Agent",
    category: "Influencer",
    deliverable_type: "influencer_collaboration_plan",
    required_sections: ["Creator profile", "Collaboration angle", "Outreach message", "Approval notes"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: true,
    supports_execution_actions: true,
    minimum_quality_standard: "Brand-safe creator collaboration plan.",
  },
  {
    agent_key: "integration_automation_agent",
    display_name: "Integration / Automation Agent",
    category: "Internal",
    deliverable_type: "automation_plan",
    required_sections: ["Integration objective", "System mapping", "Automation steps", "Risk controls"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: true,
    minimum_quality_standard: "Governed automation plan with safe operational boundaries.",
  },
  {
    agent_key: "security_compliance_agent",
    display_name: "Security & Compliance Agent",
    category: "Internal",
    deliverable_type: "security_compliance_report",
    required_sections: ["Risk summary", "Control status", "Required action", "Owner decision"],
    client_safe: true,
    owner_approval_required_for_external_action: true,
    supports_media_assets: false,
    supports_execution_actions: false,
    minimum_quality_standard: "Security-conscious output with no credential exposure.",
  },
];

export function getAgentOutputContract(agentKey: unknown): AgentOutputContract {
  const key = String(agentKey || "").trim();

  return (
    ALL_AGENT_OUTPUT_CONTRACTS.find((contract) => contract.agent_key === key) ||
    {
      agent_key: key || "unknown_agent",
      display_name: key || "Unknown Agent",
      category: "General",
      deliverable_type: "general_client_deliverable",
      required_sections: DEFAULT_REQUIRED_SECTIONS,
      client_safe: true,
      owner_approval_required_for_external_action: true,
      supports_media_assets: false,
      supports_execution_actions: true,
      minimum_quality_standard: "Client-ready, action-oriented, non-generic output.",
    }
  );
}

function normaliseText(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value);
  } catch {
    return "";
  }
}

export function validateAgentOutputContract(
  agentKey: unknown,
  payload: Record<string, unknown>
): ContractValidationResult {
  const contract = getAgentOutputContract(agentKey);
  const outputText = normaliseText(
    payload.output ||
    payload.deliverable ||
    payload.latest_deliverable ||
    payload.generated_output ||
    payload.final_output ||
    payload.result ||
    payload.data
  ).toLowerCase();

  const missingSections = contract.required_sections.filter((section) => {
    const label = section.toLowerCase();
    return !outputText.includes(label);
  });

  const hasMeaningfulOutput = outputText.trim().length >= 80;
  const qualityPassed = hasMeaningfulOutput && missingSections.length <= Math.ceil(contract.required_sections.length / 2);

  return {
    success: true,
    all_agent_output_contracts_enabled: true,
    agent_key: contract.agent_key,
    contract_found: Boolean(
      ALL_AGENT_OUTPUT_CONTRACTS.find((item) => item.agent_key === contract.agent_key)
    ),
    contract,
    missing_sections: missingSections,
    quality_passed: qualityPassed,
    client_safe: true,
    output_contract_status: qualityPassed ? "passed" : "needs_revision",
    output_contract_reason: qualityPassed
      ? "Output satisfies the minimum client-ready contract."
      : "Output should be strengthened against the agent output contract before final delivery.",
  };
}

export function attachAgentOutputContract(
  payload: Record<string, unknown>
): Record<string, unknown> {
  const agentKey =
    payload.agent_key ||
    payload.agent ||
    payload.assigned_agent ||
    payload.selected_agent ||
    "unknown_agent";

  const validation = validateAgentOutputContract(agentKey, payload);

  return {
    ...payload,
    all_agent_output_contracts_enabled: true,
    agent_output_contract: validation.contract,
    agent_output_contract_validation: validation,
    output_contract_status: validation.output_contract_status,
    output_contract_quality_passed: validation.quality_passed,
    client_safe: true,
  };
}
