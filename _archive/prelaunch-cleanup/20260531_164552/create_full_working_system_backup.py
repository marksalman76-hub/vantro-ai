from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BACKUP_ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform-system-backups")
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_name = f"ecommerce_ai_agent_platform_working_backup_{stamp}"
backup_dir = BACKUP_ROOT / backup_name
backup_dir.mkdir(parents=True, exist_ok=True)

exclude_dirs = {
    ".git",
    "node_modules",
    ".next",
    ".vercel",
    "__pycache__",
    ".venv",
    "venv",
}

exclude_files_suffix = {
    ".pyc",
    ".pyo",
    ".log",
}

def ignore_func(dir_path, names):
    ignored = []
    for name in names:
        p = Path(dir_path) / name
        if name in exclude_dirs:
            ignored.append(name)
        elif p.is_file() and p.suffix in exclude_files_suffix:
            ignored.append(name)
    return ignored

project_copy = backup_dir / "project_source"
shutil.copytree(ROOT, project_copy, ignore=ignore_func)

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, cwd=ROOT, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        return e.output

metadata = {
    "backup_created_at": datetime.now().isoformat(),
    "source_project": str(ROOT),
    "backup_folder": str(backup_dir),
    "git_log_latest_10": run_cmd("git log --oneline -10"),
    "git_status": run_cmd("git status"),
    "current_branch": run_cmd("git branch --show-current").strip(),
    "latest_commit": run_cmd("git rev-parse HEAD").strip(),
    "notes": [
        "Full working source backup created after UI declutter and compact execution workspace stabilisation.",
        "Excluded node_modules, .next, .git, .vercel, virtual environments, pycache, and compiled bytecode.",
        "Repository history remains available remotely through GitHub.",
    ],
}

(backup_dir / "BACKUP_METADATA.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
(backup_dir / "GIT_STATUS.txt").write_text(metadata["git_status"], encoding="utf-8")
(backup_dir / "LATEST_COMMITS.txt").write_text(metadata["git_log_latest_10"], encoding="utf-8")

zip_base = BACKUP_ROOT / backup_name
zip_path = shutil.make_archive(str(zip_base), "zip", backup_dir)

print("FULL_WORKING_SYSTEM_BACKUP_CREATED")
print(f"Backup folder: {backup_dir}")
print(f"Backup ZIP: {zip_path}")
print(f"Latest commit: {metadata['latest_commit']}")
print("Excluded: .git, node_modules, .next, .vercel, virtualenvs, pycache, bytecode")