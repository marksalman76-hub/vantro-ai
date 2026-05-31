from pathlib import Path
import json
import os
import re

ROOT = Path(__file__).resolve().parent

FILES_TO_CHECK = [
    "render.yaml",
    "Dockerfile",
    "Procfile",
    "backend/app/main.py",
    "backend/app/runtime/execution_queue_runtime.py",
    "backend/app/runtime/provider_execution_persistence.py",
    "backend/app/runtime/provider_connector_registry.py",
    "backend/app/runtime/delegated_workforce_execution.py",
    "backend/app/runtime/real_action_execution_bridge.py",
]

def read(path):
    p = ROOT / path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

def exists(path):
    return (ROOT / path).exists()

def scan_text():
    combined = {}
    for file in FILES_TO_CHECK:
        combined[file] = read(file)
    return combined

def main():
    texts = scan_text()
    all_text = "\n".join(texts.values()).lower()

    checks = {
        "render_yaml_exists": exists("render.yaml"),
        "dockerfile_exists": exists("Dockerfile"),
        "procfile_exists": exists("Procfile"),
        "uses_uvicorn": "uvicorn" in all_text,
        "uses_gunicorn": "gunicorn" in all_text,
        "worker_count_configured": bool(re.search(r"workers|WEB_CONCURRENCY|--workers", all_text, re.I)),
        "redis_referenced": "redis" in all_text,
        "postgres_referenced": any(x in all_text for x in ["postgres", "postgresql", "database_url"]),
        "queue_runtime_present": exists("backend/app/runtime/execution_queue_runtime.py"),
        "provider_persistence_present": exists("backend/app/runtime/provider_execution_persistence.py"),
        "rate_limit_referenced": any(x in all_text for x in ["rate limit", "ratelimit", "slowapi", "throttle"]),
        "health_route_present": "/health" in all_text,
        "readiness_route_present": any(x in all_text for x in ["/ready", "/readiness", "readiness"]),
        "background_worker_referenced": any(x in all_text for x in ["worker", "background", "queue"]),
        "external_action_bridge_present": exists("backend/app/runtime/real_action_execution_bridge.py"),
    }

    recommendations = []

    if checks["uses_uvicorn"] and not checks["uses_gunicorn"]:
        recommendations.append("Add production process runner strategy: Gunicorn with Uvicorn workers or equivalent multi-worker Render command.")
    if not checks["worker_count_configured"]:
        recommendations.append("Define WEB_CONCURRENCY or explicit worker count for production backend scaling.")
    if not checks["redis_referenced"]:
        recommendations.append("Add Redis or equivalent managed queue/broker for distributed execution and retry isolation.")
    if not checks["readiness_route_present"]:
        recommendations.append("Separate /health from deeper /readiness so edge checks are cheap under load.")
    if not checks["rate_limit_referenced"]:
        recommendations.append("Add controlled rate shaping and per-route limits instead of allowing edge-layer rejection to dominate.")
    if checks["queue_runtime_present"]:
        recommendations.append("Promote queue runtime into dedicated worker process for provider/external execution offload.")

    score = sum(1 for v in checks.values() if v is True)
    total = len(checks)

    report = {
        "audit": "production_scaling_readiness",
        "score": f"{score}/{total}",
        "checks": checks,
        "recommendations": recommendations,
        "safe_next_build": [
            "Add production process command documentation and worker scaling config.",
            "Add separate lightweight readiness route if missing.",
            "Add scaling runbook file without changing live runtime.",
            "Prepare Redis-backed queue migration plan before code activation.",
        ],
        "status": "SCALING_FOUNDATION_AUDIT_COMPLETE",
    }

    out = ROOT / "production_scaling_readiness_audit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("PRODUCTION_SCALING_READINESS_AUDIT_COMPLETE")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()