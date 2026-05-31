import json
import time
import urllib.request
import urllib.error
from pathlib import Path

TARGETS = {
    "frontend_home": "https://app.trance-formation.com.au/",
    "frontend_client": "https://app.trance-formation.com.au/client",
    "frontend_admin": "https://app.trance-formation.com.au/admin",
    "frontend_signup": "https://app.trance-formation.com.au/signup",
    "frontend_support": "https://app.trance-formation.com.au/support-request",
    "backend_health": "https://api.trance-formation.com.au/health",
}

def probe(name, url, timeout=25):
    started = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "final-render-smoke-verifier/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read(3000).decode("utf-8", errors="replace")
            return {
                "name": name,
                "url": url,
                "ok": 200 <= res.status < 400,
                "status": res.status,
                "elapsed_ms": round((time.time() - started) * 1000, 2),
                "body_preview": body[:500],
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(3000).decode("utf-8", errors="replace")
        return {
            "name": name,
            "url": url,
            "ok": False,
            "status": exc.code,
            "elapsed_ms": round((time.time() - started) * 1000, 2),
            "body_preview": body[:500],
        }
    except Exception as exc:
        return {
            "name": name,
            "url": url,
            "ok": False,
            "status": None,
            "elapsed_ms": round((time.time() - started) * 1000, 2),
            "error": repr(exc),
        }

def main():
    results = [probe(name, url) for name, url in TARGETS.items()]
    passed = sum(1 for r in results if r["ok"])
    total = len(results)

    report = {
        "verification": "final_render_smoke_verification",
        "score": f"{passed}/{total}",
        "results": results,
        "live_runtime_changed": False,
        "destructive_action_performed": False,
        "status": "FINAL_RENDER_SMOKE_VERIFICATION_PASSED" if passed == total else "FINAL_RENDER_SMOKE_VERIFICATION_NEEDS_REVIEW",
    }

    Path("final_render_smoke_verification_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("FINAL_RENDER_SMOKE_VERIFICATION_COMPLETE")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()