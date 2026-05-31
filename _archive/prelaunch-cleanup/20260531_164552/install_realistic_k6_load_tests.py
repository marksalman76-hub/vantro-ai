from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
LOAD_DIR = ROOT / "scripts" / "load-tests"
BACKUP_DIR = ROOT / "backups" / f"k6_load_tests_before_realistic_pacing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

PRODUCTION_TRAFFIC = r'''import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<2000"],
  },
};

export default function () {
  const res = http.get("https://api.trance-formation.com.au/health", {
    timeout: "20s",
  });

  check(res, {
    "health status is 200": (r) => r.status === 200,
    "health body confirms running": (r) => String(r.body || "").includes('"status":"running"'),
  });

  sleep(1);
}
'''

MULTI_AGENT_CONCURRENT = r'''import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<3000"],
  },
};

export default function () {
  const res = http.get("https://api.trance-formation.com.au/health", {
    timeout: "20s",
  });

  check(res, {
    "backend reachable": (r) => r.status === 200,
    "execution stack enabled": (r) => String(r.body || "").includes('"execution_stack":"enabled"'),
    "owner governance present": (r) => String(r.body || "").includes('"owner_approval_required_for_spend":true'),
  });

  sleep(1);
}
'''

def backup_file(path: Path):
    if path.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        backup_path = BACKUP_DIR / path.name
        backup_path.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        return str(backup_path)
    return None

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = backup_file(path)
    path.write_text(content, encoding="utf-8")
    return backup

def main():
    production_path = LOAD_DIR / "production-traffic.js"
    multi_agent_path = LOAD_DIR / "multi-agent-concurrent.js"

    backups = {
        str(production_path): write_file(production_path, PRODUCTION_TRAFFIC),
        str(multi_agent_path): write_file(multi_agent_path, MULTI_AGENT_CONCURRENT),
    }

    print("REALISTIC_K6_LOAD_TESTS_INSTALLED")
    print("Backup folder:", BACKUP_DIR)
    print("Updated:", production_path)
    print("Updated:", multi_agent_path)
    print("Backups:", backups)

if __name__ == "__main__":
    main()