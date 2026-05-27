from __future__ import annotations

from typing import Any, Dict, List, Optional


CLIENT_FACING_AGENTS = [
    {"key": "head_agent", "name": "Head Agent / CEO", "category": "core_control", "enterprise_only": True},
    {"key": "strategist_agent", "name": "Strategist Agent", "category": "core_control", "enterprise_only": False},

    {"key": "business_growth_partnerships_agent", "name": "Business Growth & Partnerships Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "lead_generator_agent", "name": "Lead Generator / Appointment Setter Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "marketing_specialist_agent", "name": "Marketing Specialist Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "social_media_content_agent", "name": "Social Media Manager / Content Creator Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "seo_agent", "name": "SEO Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "email_reply_agent", "name": "Email Reply Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "crm_agent", "name": "CRM AI Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "sales_closer_agent", "name": "Sales / Closer Agent", "category": "business_growth_engine", "enterprise_only": False},

    {"key": "receptionist_agent", "name": "Receptionist Agent", "category": "frontline_operations", "enterprise_only": False},

    {"key": "website_app_agent", "name": "Custom Websites / Landing Pages / Apps Agent", "category": "product_delivery", "enterprise_only": False},
    {"key": "product_development_agent", "name": "Product Development Agent", "category": "product_delivery", "enterprise_only": False},
    {"key": "ecommerce_agent", "name": "E-commerce Agent", "category": "product_delivery", "enterprise_only": False},

    {"key": "demo_trial_agent", "name": "Demo / Trial Agent", "category": "scale_system_agents", "enterprise_only": False},

    {"key": "influencer_outreach_agent", "name": "Influencer Outreach Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "ugc_media_agent", "name": "UGC / AI Media Agent", "category": "media_generation", "enterprise_only": False},
    {"key": "analytics_agent", "name": "Analytics & Reporting Agent", "category": "analytics_intelligence", "enterprise_only": False},
    {"key": "ads_optimisation_agent", "name": "Ads Optimisation Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "customer_success_agent", "name": "Customer Success Agent", "category": "frontline_operations", "enterprise_only": False},
    {"key": "operations_agent", "name": "Operations Agent", "category": "operations", "enterprise_only": False},
    {"key": "finance_admin_agent", "name": "Finance / Admin Agent", "category": "operations", "enterprise_only": False},
    {"key": "research_agent", "name": "Research Agent", "category": "analytics_intelligence", "enterprise_only": False},
    {"key": "content_strategy_agent", "name": "Content Strategy Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "retention_loyalty_agent", "name": "Retention / Loyalty Agent", "category": "business_growth_engine", "enterprise_only": False},
    {"key": "review_reputation_agent", "name": "Reviews / Reputation Agent", "category": "frontline_operations", "enterprise_only": False},
    {"key": "workflow_automation_agent", "name": "Workflow Automation Agent", "category": "operations", "enterprise_only": False},
]

SYSTEM_AGENTS = [
    {"key": "orchestration_agent", "name": "Orchestration Agent", "category": "system_orchestration", "enterprise_only": True},
    {"key": "security_compliance_agent", "name": "Security & Compliance Agent", "category": "system_governance", "enterprise_only": True},
    {"key": "qa_testing_agent", "name": "QA / Testing Agent", "category": "system_quality", "enterprise_only": True},
    {"key": "integration_automation_agent", "name": "Integration / Automation Agent", "category": "system_integrations", "enterprise_only": True},
    {"key": "billing_optimisation_agent", "name": "Billing Optimisation Agent", "category": "system_billing", "enterprise_only": True},
    {"key": "training_learning_agent", "name": "Training / Learning Agent", "category": "system_learning", "enterprise_only": True},
]

RUNTIME_INTELLIGENCE_COMPONENTS = [
    {"key": "global_output_quality_runtime", "name": "Global Output Quality Runtime", "category": "quality_runtime"},
    {"key": "gold_standard_benchmark_runtime", "name": "Gold-Standard Benchmark Runtime", "category": "quality_runtime"},
    {"key": "outcome_learning_runtime", "name": "Outcome Learning Runtime", "category": "learning_runtime"},
    {"key": "provider_health_failover_runtime", "name": "Provider Health + Failover Runtime", "category": "provider_runtime"},
    {"key": "background_worker_loop_runtime", "name": "Background Worker Loop Runtime", "category": "execution_runtime"},
    {"key": "asset_storage_delivery_runtime", "name": "Asset Storage + Signed Delivery Runtime", "category": "delivery_runtime"},
    {"key": "controlled_openai_live_execution_gate", "name": "Controlled OpenAI Live Execution Gate", "category": "provider_runtime"},
    {"key": "execution_ledger_runtime", "name": "Execution Ledger Runtime", "category": "audit_runtime"},
    {"key": "postgres_ledger_bridge", "name": "Postgres Ledger Bridge", "category": "persistence_runtime"},
    {"key": "dispatch_policy_worker_runtime", "name": "Dispatch Policy Worker Runtime", "category": "execution_runtime"},
]

HIDDEN_INTERNAL_LAYERS = [
    {"key": "entitlement_guard", "name": "Entitlement Guard", "client_visible": False},
    {"key": "approval_governance_layer", "name": "Approval Governance Layer", "client_visible": False},
    {"key": "tenant_isolation_layer", "name": "Tenant Isolation Layer", "client_visible": False},
    {"key": "credential_safety_layer", "name": "Credential Safety Layer", "client_visible": False},
    {"key": "audit_visibility_layer", "name": "Audit Visibility Layer", "client_visible": False},
]


def list_real_agent_component_catalogue() -> Dict[str, Any]:
    return {
        "platform_label": "unique_multi_agent_multi_industry_platform",
        "client_facing_agents": CLIENT_FACING_AGENTS,
        "system_agents": SYSTEM_AGENTS,
        "runtime_intelligence_components": RUNTIME_INTELLIGENCE_COMPONENTS,
        "hidden_internal_layers": HIDDEN_INTERNAL_LAYERS,
        "counts": calculate_catalogue_counts(),
        "commercial_catalogue_count": len(CLIENT_FACING_AGENTS),
        "total_visible_agent_count": len(CLIENT_FACING_AGENTS) + len(SYSTEM_AGENTS),
        "total_operational_component_count": len(CLIENT_FACING_AGENTS) + len(SYSTEM_AGENTS) + len(RUNTIME_INTELLIGENCE_COMPONENTS) + len(HIDDEN_INTERNAL_LAYERS),
        "note": "commercial catalogue count is separate from total operational intelligence/runtime count",
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def calculate_catalogue_counts() -> Dict[str, int]:
    return {
        "client_facing_agents": len(CLIENT_FACING_AGENTS),
        "system_agents": len(SYSTEM_AGENTS),
        "runtime_intelligence_components": len(RUNTIME_INTELLIGENCE_COMPONENTS),
        "hidden_internal_layers": len(HIDDEN_INTERNAL_LAYERS),
        "enterprise_only_visible_agents": sum(1 for a in CLIENT_FACING_AGENTS + SYSTEM_AGENTS if a.get("enterprise_only")),
        "client_selectable_non_enterprise_agents": sum(1 for a in CLIENT_FACING_AGENTS if not a.get("enterprise_only")),
    }


def get_catalogue_component_by_key(component_key: str) -> Dict[str, Any]:
    key = (component_key or "").strip().lower()

    for group_name, group in [
        ("client_facing_agent", CLIENT_FACING_AGENTS),
        ("system_agent", SYSTEM_AGENTS),
        ("runtime_intelligence_component", RUNTIME_INTELLIGENCE_COMPONENTS),
        ("hidden_internal_layer", HIDDEN_INTERNAL_LAYERS),
    ]:
        for item in group:
            if item.get("key") == key:
                return {
                    "found": True,
                    "component_type": group_name,
                    "component": item,
                    "credential_values_exposed": False,
                    "customer_safe": True,
                }

    return {
        "found": False,
        "component_key": key,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def list_client_selectable_agents(plan: str = "business") -> Dict[str, Any]:
    plan_key = (plan or "business").strip().lower()

    agents = []
    for agent in CLIENT_FACING_AGENTS:
        if agent.get("enterprise_only") and plan_key != "enterprise":
            continue
        agents.append(agent)

    return {
        "plan": plan_key,
        "agents": agents,
        "count": len(agents),
        "head_agent_available": any(a["key"] == "head_agent" for a in agents),
        "orchestration_agent_client_selectable": False,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def real_agent_component_catalogue_status() -> Dict[str, Any]:
    counts = calculate_catalogue_counts()
    return {
        "real_agent_component_catalogue_locked": True,
        "platform_label": "unique_multi_agent_multi_industry_platform",
        "commercial_catalogue_count": len(CLIENT_FACING_AGENTS),
        "visible_agent_count": len(CLIENT_FACING_AGENTS) + len(SYSTEM_AGENTS),
        "operational_component_count": len(CLIENT_FACING_AGENTS) + len(SYSTEM_AGENTS) + len(RUNTIME_INTELLIGENCE_COMPONENTS) + len(HIDDEN_INTERNAL_LAYERS),
        "counts": counts,
        "client_catalogue_is_not_same_as_runtime_component_count": True,
        "credential_values_exposed": False,
        "customer_safe": True,
    }
