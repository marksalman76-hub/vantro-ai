from backend.app.runtime.outcome_action_execution_runtime import create_outcome_action_plan

sample = """
4. Execution Plan with Concrete Steps
- Develop tailored value propositions and marketing materials for hospital CIOs.
- Create compliance framework outlines for HIPAA and GDPR.
- Launch targeted lead generation campaigns including webinars and whitepapers.
- Establish partnerships with healthcare technology vendors.
- Build KPI dashboard for sales pipeline and pilot engagement tracking.
5. Deliverables/Assets/Actions to Create
"""

plan = create_outcome_action_plan(
    outcome_text=sample,
    source_agent="marketing_specialist_agent",
    owner_approved=True,
)

agents = {p["recommended_agent"] for p in plan["action_packets"]}
titles = [p["title"] for p in plan["action_packets"]]

assert plan["success"] is True
assert plan["profile"] == "outcome_action_execution_plan_v2"
assert "security_compliance_agent" in agents
assert "lead_generator_appointment_setter_agent" in agents or "social_media_manager_content_creator_agent" in agents
assert "business_growth_partnerships_agent" in agents
assert "analytics_optimisation_agent" in agents
assert all("Execution Plan with Concrete Steps" not in t for t in titles)
assert all("Deliverables/Assets/Actions" not in t for t in titles)

print("OUTCOME_ACTION_EXECUTION_RUNTIME_V2_TEST_PASSED")
print({
    "action_count": plan["action_count"],
    "recommended_agents": sorted(agents),
})
