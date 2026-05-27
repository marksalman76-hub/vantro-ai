from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
MAIN = ROOT / "backend" / "app" / "main.py"

text = MAIN.read_text(encoding="utf-8")

alias_code = '''
AGENT_ALIAS_MAP: Dict[str, str] = {
    "product_intelligence_agent": "product_research_agent",
}
'''

if "AGENT_ALIAS_MAP" not in text:
    text = text.replace(
        'ACTION_TO_EXECUTION_MAP: Dict[str, str] = {',
        alias_code + '\n\nACTION_TO_EXECUTION_MAP: Dict[str, str] = {',
    )

text = text.replace(
    '''def run_agent(request: RunAgentRequest) -> Dict[str, object]:
    credit_gate = pg_client_credit_gate({''',
    '''def run_agent(request: RunAgentRequest) -> Dict[str, object]:
    requested_agent = AGENT_ALIAS_MAP.get(request.requested_agent, request.requested_agent)

    credit_gate = pg_client_credit_gate({''',
)

text = text.replace(
    '''    if not agent_exists(request.requested_agent):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
        }''',
    '''    if not agent_exists(requested_agent):
        return {
            "success": False,
            "error": "unknown_agent",
            "requested_agent": request.requested_agent,
            "normalised_agent": requested_agent,
        }''',
)

text = text.replace(
    '''        if request.requested_agent not in active_agents:
            return {
                "success": False,
                "error": "agent_not_active_for_tenant",
                "tenant_id": request.tenant_id,
                "requested_agent": request.requested_agent,
            }''',
    '''        normalised_active_agents = [
            AGENT_ALIAS_MAP.get(agent, agent) for agent in active_agents
        ]

        if requested_agent not in normalised_active_agents:
            return {
                "success": False,
                "error": "agent_not_active_for_tenant",
                "tenant_id": request.tenant_id,
                "requested_agent": request.requested_agent,
                "normalised_agent": requested_agent,
            }''',
)

text = text.replace(
    "requested_agent=request.requested_agent,",
    "requested_agent=requested_agent,",
)

text = text.replace(
    "title=f\"{request.requested_agent} execution\",",
    "title=f\"{requested_agent} execution\",",
)

MAIN.write_text(text, encoding="utf-8")

print("STEP_192_AGENT_ALIAS_NORMALISATION_INSTALLED")
print("product_intelligence_agent -> product_research_agent")
print("STEP_192_OK")