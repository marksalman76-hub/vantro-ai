"""
OpenAI SDK Dependency Guard

Checks whether the OpenAI Python SDK is installed without making any live call
and without exposing credentials, prompts, backend configuration, or internals.
"""

from importlib.util import find_spec
from typing import Dict


class OpenAISDKDependencyGuard:
    def check(self) -> Dict[str, object]:
        installed = find_spec("openai") is not None

        return {
            "success": True,
            "dependency": "openai",
            "installed": installed,
            "live_call_attempted": False,
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
            "safe_status": (
                "OpenAI SDK is installed."
                if installed
                else "OpenAI SDK is not installed. Install with: pip install openai"
            ),
        }


openai_sdk_dependency_guard = OpenAISDKDependencyGuard()
