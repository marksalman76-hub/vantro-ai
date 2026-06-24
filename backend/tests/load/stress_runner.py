"""
Standalone asyncio stress runner — Vantro AI Platform
======================================================
Ramps concurrency from 10 → 100 → 500 → 1000 and reports latency percentiles.

Usage:
    python tests/load/stress_runner.py --host http://localhost:8000
    python tests/load/stress_runner.py --host https://api.vantro.ai --max-users 500

Requires: pip install httpx
"""

import argparse
import asyncio
import statistics
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field

import httpx


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class RequestResult:
    endpoint: str
    status: int
    latency_ms: float
    error: str = ""


@dataclass
class ScenarioReport:
    concurrency: int
    duration_s: float
    results: list[RequestResult] = field(default_factory=list)

    def summary(self) -> dict:
        lats = [r.latency_ms for r in self.results]
        errors = [r for r in self.results if r.status >= 500 or r.error]
        ok = [r for r in self.results if r.status < 400]
        by_endpoint: dict[str, list[float]] = defaultdict(list)
        for r in self.results:
            by_endpoint[r.endpoint].append(r.latency_ms)
        return {
            "concurrency": self.concurrency,
            "total_requests": len(self.results),
            "ok": len(ok),
            "errors": len(errors),
            "error_rate_pct": round(len(errors) / max(len(self.results), 1) * 100, 2),
            "throughput_rps": round(len(self.results) / self.duration_s, 1),
            "p50_ms": round(statistics.median(lats), 1) if lats else 0,
            "p95_ms": round(_percentile(lats, 95), 1) if lats else 0,
            "p99_ms": round(_percentile(lats, 99), 1) if lats else 0,
            "max_ms": round(max(lats), 1) if lats else 0,
            "by_endpoint": {
                ep: {
                    "n": len(v),
                    "p50": round(statistics.median(v), 1),
                    "p95": round(_percentile(v, 95), 1),
                }
                for ep, v in sorted(by_endpoint.items())
            },
        }


def _percentile(data: list[float], p: int) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * p / 100)
    return sorted_data[min(idx, len(sorted_data) - 1)]


# ── HTTP helpers ─────────────────────────────────────────────────────────────

async def register_and_login(client: httpx.AsyncClient, host: str) -> str:
    """Register a fresh user and return bearer token."""
    email = f"stress_{uuid.uuid4().hex[:12]}@vantro.test"
    pw = "StressRun1!"
    r = await client.post(f"{host}/api/auth/register",
                          json={"email": email, "password": pw, "name": "Stress"})
    if r.status_code not in (200, 201):
        return ""
    data = r.json()
    return data.get("access_token", "")


async def timed_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    label: str,
    **kwargs,
) -> RequestResult:
    t0 = time.perf_counter()
    try:
        r = await getattr(client, method)(url, **kwargs)
        latency = (time.perf_counter() - t0) * 1000
        return RequestResult(endpoint=label, status=r.status_code, latency_ms=latency)
    except Exception as exc:
        latency = (time.perf_counter() - t0) * 1000
        return RequestResult(endpoint=label, status=0, latency_ms=latency, error=str(exc))


# ── Scenario: health endpoint at scale ───────────────────────────────────────

async def scenario_health(host: str, concurrency: int) -> ScenarioReport:
    """Hammer /health with N concurrent requests."""
    async with httpx.AsyncClient(timeout=10) as client:
        t0 = time.perf_counter()
        results = await asyncio.gather(*[
            timed_request(client, "get", f"{host}/health", "/health")
            for _ in range(concurrency)
        ])
        return ScenarioReport(
            concurrency=concurrency,
            duration_s=time.perf_counter() - t0,
            results=list(results),
        )


# ── Scenario: authenticated agent job submission at scale ─────────────────────

async def scenario_agent_run(host: str, concurrency: int) -> ScenarioReport:
    """
    Register `concurrency` users, then have them all submit an agent job
    simultaneously.
    """
    tokens: list[str] = []
    async with httpx.AsyncClient(timeout=30) as client:
        # Sequential registration (avoid hammering auth in setup)
        for i in range(min(concurrency, 50)):
            tok = await register_and_login(client, host)
            if tok:
                tokens.append(tok)

        if not tokens:
            print("  ⚠  No tokens obtained — is the server running?")
            return ScenarioReport(concurrency=concurrency, duration_s=0)

        async def one_run(token: str) -> RequestResult:
            return await timed_request(
                client, "post",
                f"{host}/api/agents/receptionist_agent/run",
                "/api/agents/{id}/run",
                json={"prompt": "Stress test concurrent run", "context": {}},
                headers={"Authorization": f"Bearer {token}"},
            )

        t0 = time.perf_counter()
        # Reuse tokens cyclically if concurrency > number of registered users
        results = await asyncio.gather(*[
            one_run(tokens[i % len(tokens)]) for i in range(concurrency)
        ])
        return ScenarioReport(
            concurrency=concurrency,
            duration_s=time.perf_counter() - t0,
            results=list(results),
        )


# ── Scenario: realistic multi-endpoint user session ───────────────────────────

async def scenario_full_session(host: str, concurrency: int) -> ScenarioReport:
    """
    Each virtual user: login → run agent → poll status × 3 → list jobs.
    Simulates the complete client dashboard flow.
    """
    tokens: list[str] = []
    async with httpx.AsyncClient(timeout=30) as client:
        for _ in range(min(concurrency, 50)):
            tok = await register_and_login(client, host)
            if tok:
                tokens.append(tok)

        if not tokens:
            return ScenarioReport(concurrency=concurrency, duration_s=0)

        async def session(token: str) -> list[RequestResult]:
            hdrs = {"Authorization": f"Bearer {token}"}
            out = []

            # Run agent
            r = await timed_request(
                client, "post",
                f"{host}/api/agents/receptionist_agent/run",
                "run_agent",
                json={"prompt": "Full session stress test", "context": {}},
                headers=hdrs,
            )
            out.append(r)
            job_id = ""
            if r.status in (200, 201):
                try:
                    body = (await client.post(
                        f"{host}/api/agents/receptionist_agent/run",
                        json={"prompt": "poll", "context": {}},
                        headers=hdrs,
                    )).json()
                    job_id = body.get("job_id", "")
                except Exception:
                    pass

            # Poll status 3 times
            for _ in range(3):
                if job_id:
                    out.append(await timed_request(
                        client, "get",
                        f"{host}/api/agents/jobs/{job_id}",
                        "poll_status",
                        headers=hdrs,
                    ))
                await asyncio.sleep(0.1)

            # List jobs
            out.append(await timed_request(
                client, "get",
                f"{host}/api/agents/jobs",
                "list_jobs",
                headers=hdrs,
            ))
            return out

        t0 = time.perf_counter()
        all_results = await asyncio.gather(*[
            session(tokens[i % len(tokens)]) for i in range(concurrency)
        ])
        flat = [r for session_results in all_results for r in session_results]
        return ScenarioReport(
            concurrency=concurrency,
            duration_s=time.perf_counter() - t0,
            results=flat,
        )


# ── Runner ────────────────────────────────────────────────────────────────────

def _print_report(report: ScenarioReport, label: str) -> None:
    s = report.summary()
    bar = "━" * 60
    print(f"\n{bar}")
    print(f"  {label}  |  concurrency={s['concurrency']}")
    print(bar)
    print(f"  Total requests : {s['total_requests']}")
    print(f"  OK (2xx/3xx)   : {s['ok']}")
    print(f"  Errors         : {s['errors']}  ({s['error_rate_pct']}%)")
    print(f"  Throughput     : {s['throughput_rps']} req/s")
    print(f"  p50 latency    : {s['p50_ms']} ms")
    print(f"  p95 latency    : {s['p95_ms']} ms")
    print(f"  p99 latency    : {s['p99_ms']} ms")
    print(f"  Max latency    : {s['max_ms']} ms")
    if s["by_endpoint"]:
        print("  Breakdown:")
        for ep, stats in s["by_endpoint"].items():
            print(f"    {ep:<35} n={stats['n']:4d}  p50={stats['p50']:6.0f}ms  p95={stats['p95']:6.0f}ms")


async def main(host: str, max_users: int) -> None:
    print(f"\n🔥 Vantro Stress Runner — target: {host}")
    print(f"   Ramp: 10 → 50 → 100 → {max_users} concurrent users\n")

    ramp_levels = [10, 50, 100]
    if max_users > 100:
        ramp_levels.append(max_users)

    # --- Phase 1: Health endpoint (baseline) ---
    print("Phase 1: Health endpoint baseline")
    for c in ramp_levels:
        r = await scenario_health(host, c)
        _print_report(r, f"GET /health  ×{c}")

    # --- Phase 2: Agent job submission ---
    print("\nPhase 2: Concurrent agent job submission")
    for c in [10, 50, min(100, max_users)]:
        print(f"  Spinning up {c} concurrent job submissions …")
        r = await scenario_agent_run(host, c)
        _print_report(r, f"POST /agents/{{id}}/run  ×{c}")

    # --- Phase 3: Full user session ---
    print("\nPhase 3: Full authenticated user sessions")
    for c in [10, min(50, max_users)]:
        print(f"  Running {c} full sessions concurrently …")
        r = await scenario_full_session(host, c)
        _print_report(r, f"Full session ×{c}")

    print("\n✅ Stress run complete.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vantro stress runner")
    parser.add_argument("--host", default="http://localhost:8000",
                        help="API base URL")
    parser.add_argument("--max-users", type=int, default=100,
                        help="Peak concurrency level")
    args = parser.parse_args()
    asyncio.run(main(args.host, args.max_users))
