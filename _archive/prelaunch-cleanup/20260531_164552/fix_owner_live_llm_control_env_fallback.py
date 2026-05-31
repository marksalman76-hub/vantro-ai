from pathlib import Path
from datetime import datetime

path = Path("backend/app/core/owner_live_llm_control.py")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups") / ("owner_live_llm_control_env_fallback_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "owner_live_llm_control.py"
backup.write_text(text, encoding="utf-8")

text = text.replace("import json\n", "import json\nimport os\n")

old = '''    def is_enabled(self) -> bool:
        return bool(self.get_state().get("live_llm_execution_enabled", False))
'''

new = '''    def is_enabled(self) -> bool:
        env_enabled = str(os.getenv("OWNER_LIVE_EXECUTION_ENABLED", "")).strip().lower() in {"1", "true", "yes", "on", "enabled"}
        real_provider_enabled = str(os.getenv("ENABLE_REAL_PROVIDER_EXECUTION", "")).strip().lower() in {"1", "true", "yes", "on", "enabled"}
        live_llm_enabled = str(os.getenv("ENABLE_LIVE_LLM_CALLS", "")).strip().lower() in {"1", "true", "yes", "on", "enabled"}

        if env_enabled or real_provider_enabled or live_llm_enabled:
            return True

        return bool(self.get_state().get("live_llm_execution_enabled", False))
'''

if old not in text:
    raise SystemExit("TARGET_BLOCK_NOT_FOUND")

path.write_text(text.replace(old, new), encoding="utf-8")

print("OWNER_LIVE_LLM_CONTROL_ENV_FALLBACK_PATCHED")
print("Backup:", backup)