from pathlib import Path
import re

p = Path("frontend/src/app/admin/live-execution/page.tsx")
s = p.read_text(encoding="utf-8")

start = s.find("const AGENTS")
end = s.find("];", start)
if start == -1 or end == -1:
    raise SystemExit("Could not find AGENTS list.")
end += 2

agents = '''const AGENTS: [string, string][] = [
  ["marketing_specialist_agent", "Marketing Specialist Agent"],
  ["product_copywriting_agent", "Product Copywriting Agent"],
  ["ugc_creative_agent", "UGC Creative Agent"],
  ["seo_agent", "SEO Agent"],
  ["crm_ai_agent", "CRM AI Agent"],
  ["email_reply_agent", "Email Reply Agent"],
  ["paid_ads_agent", "Paid Ads Agent"],
  ["product_image_agent", "Product Image Agent"],
  ["influencer_collaboration_agent", "Influencer Collaboration Agent"],
  ["head_agent", "Head Agent"],
  ["strategist_agent", "Strategist Agent"],
  ["business_growth_partnerships_agent", "Business Growth & Partnerships Agent"],
  ["lead_generator_appointment_setter_agent", "Lead Generator / Appointment Setter Agent"],
  ["sales_closer_agent", "Sales / Closer Agent"],
  ["receptionist_agent", "Receptionist Agent"],
  ["customer_support_agent", "Customer Support Agent"],
  ["ecommerce_agent", "Ecommerce Agent"],
  ["product_research_agent", "Product Research Agent"],
  ["competitor_intelligence_agent", "Competitor Intelligence Agent"],
  ["brand_strategy_agent", "Brand Strategy Agent"],
  ["store_builder_agent", "Store Builder Agent"],
  ["website_landing_apps_agent", "Website / Landing Page / Apps Agent"],
  ["product_development_agent", "Product Development Agent"],
  ["analytics_optimisation_agent", "Analytics Optimisation Agent"],
  ["orchestration_agent", "Orchestration Agent"],
  ["security_compliance_agent", "Security & Compliance Agent"],
  ["integration_automation_agent", "Integration / Automation Agent"],
  ["billing_optimisation_agent", "Billing Optimisation Agent"],
  ["training_learning_agent", "Training / Learning Agent"],
];'''

s = s[:start] + agents + s[end:]

helper = r'''
function inferAutonomousActionType(task: string, selectedAgent: string): string {
  const t = `${selectedAgent} ${task}`.toLowerCase();
  if (selectedAgent === "website_landing_apps_agent" || t.includes("landing page") || t.includes("website") || t.includes("web page")) return "website_draft_page";
  if (selectedAgent === "store_builder_agent" || selectedAgent === "ecommerce_agent" || t.includes("shopify") || t.includes("product page") || t.includes("store")) return "store_draft_update";
  if (selectedAgent === "paid_ads_agent" || t.includes("meta ads") || t.includes("google ads") || t.includes("ad campaign") || t.includes("campaign draft")) return "ads_campaign_draft";
  if (selectedAgent === "email_reply_agent" || t.includes("email")) return "email_draft";
  if (selectedAgent === "crm_ai_agent" || t.includes("crm")) return "crm_follow_up";
  if (selectedAgent === "seo_agent" || t.includes("seo")) return "seo_content_plan";
  if (selectedAgent === "product_image_agent" || t.includes("image")) return "product_image_generation";
  if (selectedAgent === "ugc_creative_agent" || t.includes("ugc")) return "ugc_script_draft";
  if (selectedAgent === "customer_support_agent") return "support_response_draft";
  if (selectedAgent === "receptionist_agent") return "reception_response_draft";
  if (selectedAgent === "lead_generator_appointment_setter_agent") return "lead_outreach_sequence";
  if (selectedAgent === "sales_closer_agent") return "sales_follow_up_sequence";
  return "client_deliverable";
}

function integrationsForAutonomousAgent(selectedAgent: string): string[] {
  const map: Record<string, string[]> = {
    website_landing_apps_agent: ["website", "cms"],
    store_builder_agent: ["store", "website", "cms"],
    ecommerce_agent: ["store", "website", "cms"],
    paid_ads_agent: ["ads"],
    email_reply_agent: ["email"],
    crm_ai_agent: ["crm"],
    seo_agent: ["website", "cms", "analytics"],
    product_image_agent: ["media", "asset_storage"],
    ugc_creative_agent: ["media", "asset_storage"],
    influencer_collaboration_agent: ["email", "crm"],
    lead_generator_appointment_setter_agent: ["email", "crm", "calendar"],
    sales_closer_agent: ["email", "crm"],
    receptionist_agent: ["calendar", "email"],
    customer_support_agent: ["email", "support"],
    analytics_optimisation_agent: ["analytics"],
    integration_automation_agent: ["automation"],
    billing_optimisation_agent: ["billing"],
  };
  return map[selectedAgent] || [];
}

function uniqueValues(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean)));
}
'''

if "function inferAutonomousActionType" not in s:
    s = s.replace("function buildAutonomousImplementationPlan", helper + "\nfunction buildAutonomousImplementationPlan")

# Replace buildAutonomousImplementationPlan to accept multiple agents.
s = re.sub(
    r'''function buildAutonomousImplementationPlan\(task: string, selectedAgent: string\) \{[\s\S]*?\n\}''',
    '''function buildAutonomousImplementationPlan(task: string, selectedAgents: string[] | string) {
  const cleanTask = String(task || "").trim();
  const agents = Array.isArray(selectedAgents) && selectedAgents.length ? selectedAgents : [String(selectedAgents || "marketing_specialist_agent")];

  return {
    plan_id: `portal_plan_${Date.now()}`,
    source: "portal_autonomous_execution",
    action_packets: agents.map((selectedAgent, index) => ({
      packet_id: `portal_packet_${Date.now()}_${index}`,
      title: cleanTask,
      implementation_action: inferAutonomousActionType(cleanTask, selectedAgent),
      user_requested_task: cleanTask,
      recommended_agent: selectedAgent || "marketing_specialist_agent",
      risk_level: "low",
      approval_required: false,
      execution_mode: "autonomous_governed",
      expected_output: "completed_action_evidence",
    })),
  };
}''',
    s,
    count=1,
)

# Add selectedAgents state after agent state.
s = s.replace(
'''  const [agent, setAgent] = useState("marketing_specialist_agent");''',
'''  const [agent, setAgent] = useState("marketing_specialist_agent");
  const [selectedAgents, setSelectedAgents] = useState<string[]>(["marketing_specialist_agent"]);'''
)

# Add toggle helper before runLiveExecution.
if "function toggleSelectedAgent" not in s:
    s = s.replace(
'''  async function runLiveExecution() {''',
'''  function toggleSelectedAgent(agentId: string) {
    setAgent(agentId);
    setSelectedAgents((prev) => {
      if (prev.includes(agentId)) {
        const next = prev.filter((id) => id !== agentId);
        return next.length ? next : [agentId];
      }
      return [...prev, agentId];
    });
  }

  async function runLiveExecution() {'''
    )

# Update autonomous fetch payload.
s = s.replace(
'''          implementation_plan: buildAutonomousImplementationPlan(buildStrictTaskExecutionContract(task, agentName(agent)), agent),
          owner_approved: true,
          client_owned_agents: [agent],
          package_tier: "enterprise",
          connected_integrations: ["email", "crm", "calendar"],''',
'''          implementation_plan: buildAutonomousImplementationPlan(buildStrictTaskExecutionContract(task, selectedAgents.map(agentName).join(", ")), selectedAgents),
          owner_approved: true,
          client_owned_agents: selectedAgents,
          package_tier: "enterprise",
          connected_integrations: uniqueValues(selectedAgents.flatMap(integrationsForAutonomousAgent)),'''
)

# Replace single select UI with multi-select buttons.
select_pattern = r'''<select value=\{agent\} onChange=\{\(e\) => setAgent\(e\.target\.value\)\}[\s\S]*?</select>'''
multi_ui = '''<div style={{ border: "1px solid rgba(148,163,184,.35)", borderRadius: 16, background: "#020617", padding: 12, marginBottom: 12, maxHeight: 220, overflow: "auto" }}>
                <div style={{ color: "#bfdbfe", fontSize: 12, fontWeight: 950, marginBottom: 10 }}>Select one or more agents</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2,minmax(0,1fr))", gap: 8 }}>
                  {AGENTS.map(([id, name]) => {
                    const active = selectedAgents.includes(id);
                    return (
                      <button
                        key={id}
                        type="button"
                        onClick={() => toggleSelectedAgent(id)}
                        style={{
                          textAlign: "left",
                          border: active ? "1px solid #38bdf8" : "1px solid rgba(148,163,184,.22)",
                          background: active ? "rgba(14,165,233,.18)" : "rgba(15,23,42,.55)",
                          color: "#fff",
                          borderRadius: 12,
                          padding: "9px 10px",
                          fontWeight: 850,
                          cursor: "pointer",
                          fontSize: 12,
                        }}
                      >
                        {active ? "✓ " : "+ "}{name}
                      </button>
                    );
                  })}
                </div>
              </div>'''
s = re.sub(select_pattern, multi_ui, s, count=1)

# Make displayed agent name bundle-aware.
s = s.replace('agentName(agent)', '(selectedAgents.length > 1 ? `${selectedAgents.length} agents` : agentName(agent))')

p.write_text(s, encoding="utf-8")
print("ADMIN_MULTI_AGENT_LIVE_ROUTING_FIXED")