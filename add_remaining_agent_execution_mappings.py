from pathlib import Path
from datetime import datetime

target = Path("backend/app/main.py")
text = target.read_text(encoding="utf-8")

old = '''    "major_strategy_change": "major_strategy_change",
}
'''

new = '''    "major_strategy_change": "major_strategy_change",

    # Remaining enterprise/system-safe execution mappings
    "website_strategy_generation": "governed_live_provider_generation",
    "analytics_intelligence_generation": "governed_live_provider_generation",
    "qa_testing_generation": "governed_live_provider_generation",
    "billing_optimisation_generation": "governed_live_provider_generation",
    "training_learning_generation": "governed_live_provider_generation",
}
'''

if old not in text:
    raise SystemExit("TARGET_ACTION_MAP_BLOCK_NOT_FOUND")

updated = text.replace(old, new)

backup_dir = Path("backups") / f"remaining_agent_execution_mappings_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

backup_file = backup_dir / "main.py"
backup_file.write_text(text, encoding="utf-8")

target.write_text(updated, encoding="utf-8")

print("REMAINING_AGENT_EXECUTION_MAPPINGS_ADDED")
print("Backup:", backup_file)