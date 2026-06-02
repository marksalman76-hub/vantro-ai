from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''                        body: JSON.stringify({
                          implementation_plan: buildAutonomousImplementationPlan(
                            taskValue ||
                              `Create a client-specific deliverable using the saved business profile. Business niche: ${businessProfile.business_niche || "saved business profile"}. Target audience: ${businessProfile.target_audience || "saved target audience"}. Positioning: ${businessProfile.notes || "client-specific positioning"}. Fulfil the selected agent task only and provide completion evidence.`,
                            selectedAgents
                          ),
                          client_owned_agents: selectedAgents,
                          package_tier: accountPackage || "enterprise",
                          actor_role: "client",
                          tenant_id: tenantId || "client_demo_001",
                          connected_integrations: ["media", "asset_storage", "task_store"],
                        }),
'''

new = '''                        body: JSON.stringify({
                          requested_agent: selectedAgents[0] || "paid_ads_agent",
                          workflow_stage: "client_live_execution",
                          task:
                            taskValue ||
                            `Create a client-specific deliverable using the saved business profile. Business niche: ${businessProfile.business_niche || "saved business profile"}. Target audience: ${businessProfile.target_audience || "saved target audience"}. Positioning: ${businessProfile.notes || "client-specific positioning"}. Fulfil the selected agent task only and provide completion evidence.`,
                          action_type: inferAutonomousActionType(
                            taskValue ||
                              `Create a client-specific deliverable using the saved business profile. Business niche: ${businessProfile.business_niche || "saved business profile"}. Target audience: ${businessProfile.target_audience || "saved target audience"}. Positioning: ${businessProfile.notes || "client-specific positioning"}. Fulfil the selected agent task only and provide completion evidence.`,
                            selectedAgents[0] || "paid_ads_agent"
                          ),
                          implementation_plan: buildAutonomousImplementationPlan(
                            taskValue ||
                              `Create a client-specific deliverable using the saved business profile. Business niche: ${businessProfile.business_niche || "saved business profile"}. Target audience: ${businessProfile.target_audience || "saved target audience"}. Positioning: ${businessProfile.notes || "client-specific positioning"}. Fulfil the selected agent task only and provide completion evidence.`,
                            selectedAgents
                          ),
                          client_owned_agents: selectedAgents,
                          package_tier: accountPackage || "enterprise",
                          actor_role: "client",
                          tenant_id: tenantId || "client_demo_001",
                          connected_integrations: ["media", "asset_storage", "task_store"],
                        }),
'''

if old not in text:
    raise SystemExit("client run-agent request body block not found")

text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
print("CLIENT_RUN_AGENT_REQUIRED_CONTRACT_PATCHED")