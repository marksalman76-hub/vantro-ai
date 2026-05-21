"""
Tenant Manager

Controls white-label client accounts, tenant isolation, package state,
activated agents, branding, region settings, and client-safe configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BrandProfile:
    business_name: str
    logo_url: Optional[str] = None
    primary_colour: str = "#111827"
    secondary_colour: str = "#ffffff"
    accent_colour: str = "#2563eb"
    domain: Optional[str] = None
    region: str = "Global"
    country: str = "Global"
    currency: str = "USD"
    language: str = "English"
    brand_voice: str = "premium, clear, trustworthy"


@dataclass
class Tenant:
    tenant_id: str
    company_name: str
    package_name: str
    billing_cycle: str
    status: str
    activated_agents: List[str] = field(default_factory=list)
    brand_profile: BrandProfile = field(default_factory=BrandProfile)


class TenantManager:
    def __init__(self) -> None:
        self.tenants: Dict[str, Tenant] = {}

    def create_tenant(
        self,
        tenant_id: str,
        company_name: str,
        package_name: str,
        billing_cycle: str,
        activated_agents: List[str],
        brand_profile: BrandProfile,
    ) -> Tenant:
        tenant = Tenant(
            tenant_id=tenant_id,
            company_name=company_name,
            package_name=package_name,
            billing_cycle=billing_cycle,
            status="active",
            activated_agents=activated_agents,
            brand_profile=brand_profile,
        )
        self.tenants[tenant_id] = tenant
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        return self.tenants.get(tenant_id)

    def is_tenant_active(self, tenant_id: str) -> bool:
        tenant = self.get_tenant(tenant_id)
        return bool(tenant and tenant.status == "active")

    def is_agent_active_for_tenant(self, tenant_id: str, agent_name: str) -> bool:
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        return agent_name in tenant.activated_agents

    def suspend_tenant(self, tenant_id: str) -> bool:
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        tenant.status = "suspended"
        return True

    def activate_tenant(self, tenant_id: str) -> bool:
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        tenant.status = "active"
        return True