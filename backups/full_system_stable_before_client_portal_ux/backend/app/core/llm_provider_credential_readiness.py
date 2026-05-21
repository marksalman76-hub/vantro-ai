"""
LLM Provider Credential Readiness

Checks whether approved provider credentials are configured without exposing
credential values, secrets, backend config, prompts, or provider internals.

Client-safe:
- never returns secret values
- never returns environment variable values
- never exposes provider configuration internals
"""

from dataclasses import dataclass
from typing import Dict, List
import os


@dataclass
class ProviderCredentialStatus:
    provider: str
    configured: bool
    required_key_name: str
    safe_status: str


class LLMProviderCredentialReadiness:
    def check_all(self) -> Dict[str, object]:
        providers = [
            self._check_provider("openai", "OPENAI_API_KEY"),
            self._check_provider("anthropic_claude", "ANTHROPIC_API_KEY"),
            self._check_provider("google_gemini", "GOOGLE_API_KEY"),
            self._check_provider("xai_grok", "XAI_API_KEY"),
            self._check_provider("local_or_private_model", "LOCAL_LLM_ENDPOINT"),
        ]

        configured_count = len([p for p in providers if p.configured])

        return {
            "success": True,
            "credential_values_exposed": False,
            "configured_provider_count": configured_count,
            "live_provider_execution_ready": configured_count > 0,
            "providers": [self._safe_provider_summary(p) for p in providers],
            "governance": {
                "client_secret_exposure_blocked": True,
                "backend_config_exposure_blocked": True,
                "owner_control_required": True,
                "tenant_isolation_required": True,
            },
        }

    def check_selected_provider(self, selected_provider: str) -> Dict[str, object]:
        all_status = self.check_all()
        provider_key = self._normalise_selected_provider(selected_provider)

        matching = [
            provider for provider in all_status["providers"]
            if provider["provider"] == provider_key
        ]

        selected = matching[0] if matching else {
            "provider": provider_key,
            "configured": False,
            "safe_status": "Provider route recognised but credentials are not configured yet.",
        }

        return {
            "success": True,
            "selected_provider": selected_provider,
            "normalised_provider": provider_key,
            "provider_configured": bool(selected.get("configured")),
            "provider_ready": bool(selected.get("configured")),
            "safe_status": selected.get("safe_status"),
            "credential_values_exposed": False,
            "live_execution_allowed": bool(selected.get("configured")),
            "governance": all_status["governance"],
        }

    def _check_provider(self, provider: str, required_key_name: str) -> ProviderCredentialStatus:
        configured = bool(os.getenv(required_key_name))

        return ProviderCredentialStatus(
            provider=provider,
            configured=configured,
            required_key_name=required_key_name,
            safe_status=(
                "Configured for approved live execution."
                if configured
                else "Not configured yet. Route preparation only."
            ),
        )

    def _safe_provider_summary(self, status: ProviderCredentialStatus) -> Dict[str, object]:
        return {
            "provider": status.provider,
            "configured": status.configured,
            "required_key_name": status.required_key_name,
            "safe_status": status.safe_status,
            "secret_value_exposed": False,
        }

    def _normalise_selected_provider(self, selected_provider: str) -> str:
        lowered = selected_provider.lower()

        if "openai" in lowered:
            return "openai"

        if "claude" in lowered or "anthropic" in lowered:
            return "anthropic_claude"

        if "gemini" in lowered or "google" in lowered:
            return "google_gemini"

        if "grok" in lowered or "xai" in lowered:
            return "xai_grok"

        if "local" in lowered or "private" in lowered:
            return "local_or_private_model"

        return selected_provider
