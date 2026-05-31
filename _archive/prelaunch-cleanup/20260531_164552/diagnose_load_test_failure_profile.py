from pathlib import Path
import json
import re
import urllib.request
import urllib.error
import time

ROOT = Path(__file__).resolve().parent

LOAD_TEST_FILES = [
    ROOT / "scripts" / "load-tests" / "production-traffic.js",
    ROOT / "scripts" / "load-tests" / "multi-agent-concurrent.js",
]

TARGETS = [
    "https://api.trance-formation.com.au/health",
]

def read_text(path):
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace")

def find_urls(text):
    if not text:
        return []
    return sorted(set(re.findall(r"https?://[^\s\"'`]+", text)))

def probe_url(url, timeout=20):
    started = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "platform-load-diagnostic/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read(5000).decode("utf-8", errors="replace")
            return {
                "url": url,
                "ok": 200 <= res.status < 400,
                "status": res.status,
                "elapsed_ms": round((time.time() - started) * 1000, 2),
                "body_preview": body[:500],
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(5000).decode("utf-8", errors="replace")
        return {
            "url": url,
            "ok": False,
            "status": exc.code,
            "elapsed_ms": round((time.time() - started) * 1000, 2),
            "body_preview": body[:500],
        }
    except Exception as exc:
        return {
            "url": url,
            "ok": False,
            "status": None,
            "elapsed_ms": round((time.time() - started) * 1000, 2),
            "error": repr(exc),
        }

def main():
    report = {
        "diagnostic": "load_test_failure_profile",
        "files": {},
        "discovered_urls": [],
        "probes": [],
        "assessment": [],
        "next_action": None,
    }

    discovered = set(TARGETS)

    for path in LOAD_TEST_FILES:
        text = read_text(path)
        file_report = {
            "exists": text is not None,
            "path": str(path.relative_to(ROOT)) if path.exists() else str(path),
            "size": len(text or ""),
            "contains_thresholds": "thresholds" in (text or ""),
            "contains_check": "check(" in (text or ""),
            "contains_expected_status_200": "status === 200" in (text or "") or "status == 200" in (text or ""),
            "contains_sleep": "sleep(" in (text or ""),
            "urls": find_urls(text),
            "first_2000_chars": (text or "")[:2000],
        }
        for url in file_report["urls"]:
            discovered.add(url)
        report["files"][path.name] = file_report

    report["discovered_urls"] = sorted(discovered)

    for url in report["discovered_urls"]:
        report["probes"].append(probe_url(url))

    health_probe = next((p for p in report["probes"] if "/health" in p["url"]), None)

    if health_probe and health_probe.get("ok"):
        report["assessment"].append("Public health endpoint is reachable outside k6.")
    else:
        report["assessment"].append("Public health endpoint probe failed outside k6; infrastructure or DNS should be checked before code optimisation.")

    for name, info in report["files"].items():
        if info["exists"] and not info["contains_check"]:
            report["assessment"].append(f"{name} has no explicit k6 check() block; k6 failure rate may be based on HTTP status classes rather than custom pass criteria.")
        if info["exists"] and not info["contains_sleep"]:
            report["assessment"].append(f"{name} appears to run tight loops without sleep(); this can create unrealistic request flooding and distort production readiness results.")
        if info["exists"] and info["contains_expected_status_200"]:
            report["assessment"].append(f"{name} expects HTTP 200 responses; any 401/403/404/429/5xx will be counted as failed.")

    report["next_action"] = "Review script targets and request pacing before changing backend scaling."

    out = ROOT / "load_test_failure_profile_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("LOAD_TEST_FAILURE_PROFILE_DIAGNOSTIC_COMPLETE")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()