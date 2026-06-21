# Provider registry and configuration

from .base import BaseProvider, ProviderCategory, ProviderStatus
from typing import Dict, List, Optional

class ProviderRegistry:
    """Central registry for all media providers"""

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider):
        """Register a provider"""
        self.providers[provider.name] = provider

    def get_by_category(self, category: ProviderCategory) -> List[BaseProvider]:
        """Get all providers for a category"""
        return [p for p in self.providers.values() if p.category == category]

    def get_active_by_category(self, category: ProviderCategory) -> List[BaseProvider]:
        """Get active providers for a category"""
        return [p for p in self.get_by_category(category) if p.is_ready()]

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get provider by name"""
        return self.providers.get(name)

    def status_report(self) -> Dict:
        """Get status of all providers"""
        return {
            name: {
                "status": provider.status.value,
                "category": provider.category.value,
                "ready": provider.is_ready()
            }
            for name, provider in self.providers.items()
        }

# Global registry instance
registry = ProviderRegistry()
