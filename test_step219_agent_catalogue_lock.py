import backend.app.agents.agent_registry as registry

required_agents = [
    "master_orchestrator_agent",
    "product_copywriting_agent",
    "ugc_creative_agent",
    "product_image_direction_agent",
    "influencer_collaboration_agent",
    "analytics_optimisation_agent",
]

agent_exists = getattr(registry, "agent_exists")

catalogue = (
    getattr(registry, "APPROVED_AGENTS", None)
    or getattr(registry, "AGENTS", None)
    or getattr(registry, "AGENT_REGISTRY", None)
    or getattr(registry, "AGENT_CATALOGUE", None)
    or getattr(registry, "ECOMMERCE_AGENTS", None)
)

aliases = (
    getattr(registry, "AGENT_ALIASES", None)
    or getattr(registry, "AGENT_ALIAS_MAP", None)
    or {}
)

if isinstance(catalogue, dict):
    catalogue_keys = set(catalogue.keys())
elif isinstance(catalogue, (list, tuple, set)):
    catalogue_keys = set(catalogue)
else:
    catalogue_keys = set()

checks = {}

for agent in required_agents:
    checks[f"{agent}_exists"] = agent_exists(agent) is True

checks["catalogue_count_at_least_25"] = len(catalogue_keys) >= 25
checks["aliases_safe_type"] = isinstance(aliases, dict)

print("STEP_219_AGENT_CATALOGUE_LOCK_RESULTS")
print("catalogue_count", len(catalogue_keys))
print("aliases_count", len(aliases))

for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_219_AGENT_CATALOGUE_LOCK_OK")