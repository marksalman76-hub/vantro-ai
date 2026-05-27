from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET_FILE = PROJECT_ROOT / "backend" / "app" / "core" / "owner_live_llm_control.py"

content = '''"""
Owner Live LLM Control

Persistent owner-controlled switch for allowing governed live LLM execution.

Security:
- owner/admin controlled only
- stores no credentials
- stores no prompts
- stores no backend internals
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict
import json


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CONTROL_FILE = DATA_DIR / "owner_live_llm_control.json"


DEFAULT_STATE = {
    "live_llm_execution_enabled": False,
    "updated_by": "system",
    "updated_at": None,
    "reason": "Default disabled for safety.",
    "credential_values_stored": False,
    "internal_prompts_stored": False,
    "backend_config_stored": False,
    "client_safe": True,
}


class OwnerLiveLLMControl:
    def get_state(self) -> Dict[str, object]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        if not CONTROL_FILE.exists():
            self._write_state(DEFAULT_STATE)

        return self._read_state()

    def set_state(self, enabled: bool, updated_by: str = "owner", reason: str = "") -> Dict[str, object]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        state = {
            "live_llm_execution_enabled": bool(enabled),
            "updated_by": updated_by or "owner",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason or (
                "Owner enabled governed live LLM execution."
                if enabled
                else "Owner disabled governed live LLM execution."
            ),
            "credential_values_stored": False,
            "internal_prompts_stored": False,
            "backend_config_stored": False,
            "client_safe": True,
        }

        self._write_state(state)

        return {
            "success": True,
            "state": state,
            "credential_values_stored": False,
            "internal_prompts_stored": False,
            "backend_config_stored": False,
        }

    def is_enabled(self) -> bool:
        return bool(self.get_state().get("live_llm_execution_enabled", False))

    def _read_state(self) -> Dict[str, object]:
        try:
            return json.loads(CONTROL_FILE.read_text(encoding="utf-8"))
        except Exception:
            self._write_state(DEFAULT_STATE)
            return dict(DEFAULT_STATE)

    def _write_state(self, state: Dict[str, object]) -> None:
        CONTROL_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


owner_live_llm_control = OwnerLiveLLMControl()
'''

TARGET_FILE.write_text(content, encoding="utf-8")

print("STEP_75_OWNER_LIVE_LLM_CONTROL_INSTALLED")
print(f"Created/Updated: {TARGET_FILE}")