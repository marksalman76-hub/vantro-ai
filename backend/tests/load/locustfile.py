"""
Locust load test — Vantro AI Platform
======================================
Simulates real user behaviour at scale.

Usage (against local dev):
    locust -f tests/load/locustfile.py --host=http://localhost:8000 \
           --users=500 --spawn-rate=20 --run-time=5m --headless

Usage (against staging):
    locust -f tests/load/locustfile.py --host=https://api.vantro.ai \
           --users=1000 --spawn-rate=50 --run-time=10m --headless

User mix:
    70%  ClientUser     — register → login → run agents → poll status → list jobs
    20%  BrowsingUser   — unauthenticated browsing (landing, pricing, health)
    10%  AdminUser      — admin login → review/approve HITL queue
"""

import random
import uuid

from locust import HttpUser, TaskSet, between, task, events
from locust.exception import StopUser


# ---------------------------------------------------------------------------
# Shared pool of tokens so users don't re-register every session
# ---------------------------------------------------------------------------

_TOKEN_POOL: list[str] = []
_POOL_LOCK = __import__("threading").Lock()

LOW_HITL_AGENTS = [
    "receptionist_agent",       # cost 1, starter
    "social_media_content_agent",  # cost 1, starter
    "research_agent",           # cost 2, growth
    "analytics_agent",          # cost 2, growth
    "seo_agent",                # cost 2, growth
    "content_strategy_agent",   # cost 2, growth
]

SUPPORT_TYPES = ["general", "billing", "technical", "feature_request"]


# ---------------------------------------------------------------------------
# Task sets
# ---------------------------------------------------------------------------

class AuthenticatedClientTasks(TaskSet):
    """Models a paying client: runs agents, checks status, updates profile."""

    token: str = ""
    job_ids: list[str]

    def on_start(self):
        self.job_ids = []
        # Try to grab a token from the pool first
        with _POOL_LOCK:
            if _TOKEN_POOL:
                self.token = _TOKEN_POOL.pop()
                return

        # Otherwise register + login fresh
        email = f"loadtest_{uuid.uuid4().hex}@vantro.test"
        pw = "LoadTest1!"
        r = self.client.post("/api/auth/register", json={
            "email": email, "password": pw, "name": "Load Tester"
        }, name="/api/auth/register")
        if r.status_code not in (200, 201):
            raise StopUser()

        r = self.client.post("/api/auth/login",
                             json={"email": email, "password": pw},
                             name="/api/auth/login")
        if r.status_code != 200:
            raise StopUser()
        self.token = r.json().get("access_token", "")

    def on_stop(self):
        # Return token to pool for reuse
        if self.token:
            with _POOL_LOCK:
                _TOKEN_POOL.append(self.token)

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def run_agent(self):
        agent = random.choice(LOW_HITL_AGENTS)
        prompts = [
            "Generate a weekly social content calendar for our SaaS product.",
            "Research top 5 competitors in the AI video space.",
            "Draft an outreach email for enterprise prospects.",
            "Analyse our Q3 churn data and suggest retention tactics.",
            "Create an SEO strategy for our product landing page.",
        ]
        r = self.client.post(
            f"/api/agents/{agent}/run",
            json={"prompt": random.choice(prompts), "context": {"channel": "web"}},
            headers=self._headers(),
            name="/api/agents/{agent}/run",
        )
        if r.status_code in (200, 201):
            body = r.json()
            jid = body.get("job_id")
            if jid:
                self.job_ids.append(jid)

    @task(8)
    def poll_job_status(self):
        if not self.job_ids:
            return
        jid = random.choice(self.job_ids)
        self.client.get(
            f"/api/agents/jobs/{jid}",
            headers=self._headers(),
            name="/api/agents/jobs/{id}",
        )

    @task(4)
    def list_jobs(self):
        self.client.get(
            "/api/agents/jobs?skip=0&limit=20",
            headers=self._headers(),
            name="/api/agents/jobs",
        )

    @task(2)
    def get_brand_profile(self):
        self.client.get(
            "/api/users/brand-profile",
            headers=self._headers(),
            name="/api/users/brand-profile",
        )

    @task(1)
    def update_brand_profile(self):
        tones = ["Professional", "Friendly", "Bold", "Minimal"]
        self.client.put(
            "/api/users/brand-profile",
            json={
                "business_name": f"Test Co {random.randint(1, 999)}",
                "preferred_tone": random.choice(tones),
            },
            headers=self._headers(),
            name="PUT /api/users/brand-profile",
        )

    @task(1)
    def submit_support_ticket(self):
        self.client.post(
            "/api/support/tickets",
            json={
                "ticket_type": random.choice(SUPPORT_TYPES),
                "subject": "Load test ticket",
                "detail": "This ticket was created by a load test.",
            },
            headers=self._headers(),
            name="/api/support/tickets",
        )

    @task(2)
    def list_agents(self):
        self.client.get(
            "/api/agents",
            headers=self._headers(),
            name="/api/agents",
        )


class BrowsingTasks(TaskSet):
    """Unauthenticated user browsing public endpoints."""

    @task(3)
    def health(self):
        self.client.get("/health", name="/health")

    @task(1)
    def readiness(self):
        self.client.get("/health/ready", name="/health/ready")

    @task(2)
    def root(self):
        self.client.get("/", name="/")


class AdminTasks(TaskSet):
    """Admin user monitoring and approving HITL jobs."""

    token: str = ""

    def on_start(self):
        admin_email = "admin@vantro.ai"
        admin_pw = "AdminPass1!"
        # register admin once (ignore 409)
        self.client.post("/api/auth/register", json={
            "email": admin_email, "password": admin_pw, "name": "Admin"
        }, name="/api/auth/register [admin]")

        r = self.client.post("/api/auth/login",
                             json={"email": admin_email, "password": admin_pw},
                             name="/api/auth/login [admin]")
        if r.status_code != 200:
            raise StopUser()
        self.token = r.json().get("access_token", "")

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def list_pending_approvals(self):
        self.client.get(
            "/api/admin/agents/jobs?status=pending_approval&limit=20",
            headers=self._headers(),
            name="/api/admin/agents/jobs [pending]",
        )

    @task(3)
    def list_all_users(self):
        self.client.get(
            "/api/admin/users?skip=0&limit=20",
            headers=self._headers(),
            name="/api/admin/users",
        )

    @task(2)
    def list_support_tickets(self):
        self.client.get(
            "/api/admin/support/tickets",
            headers=self._headers(),
            name="/api/admin/support/tickets",
        )

    @task(1)
    def dashboard_stats(self):
        self.client.get(
            "/api/admin/clients?limit=5",
            headers=self._headers(),
            name="/api/admin/clients",
        )


# ---------------------------------------------------------------------------
# User classes — Locust picks these based on weight
# ---------------------------------------------------------------------------

class ClientUser(HttpUser):
    tasks = [AuthenticatedClientTasks]
    weight = 70
    wait_time = between(0.5, 3.0)  # realistic think time between actions


class BrowsingUser(HttpUser):
    tasks = [BrowsingTasks]
    weight = 20
    wait_time = between(1.0, 5.0)


class AdminUser(HttpUser):
    tasks = [AdminTasks]
    weight = 10
    wait_time = between(2.0, 8.0)


# ---------------------------------------------------------------------------
# Custom event hooks — print summary stats on test end
# ---------------------------------------------------------------------------

@events.quitting.add_listener
def print_summary(environment, **kwargs):
    stats = environment.stats
    print("\n" + "="*60)
    print("VANTRO LOAD TEST SUMMARY")
    print("="*60)
    for name, entry in sorted(stats.entries.items()):
        if entry.num_requests == 0:
            continue
        p95 = entry.get_response_time_percentile(0.95)
        p99 = entry.get_response_time_percentile(0.99)
        print(
            f"{name[1]:45s}  "
            f"n={entry.num_requests:6d}  "
            f"fail={entry.num_failures:4d}  "
            f"p50={entry.median_response_time:5d}ms  "
            f"p95={p95:5d}ms  "
            f"p99={p99:5d}ms"
        )
    total = stats.total
    print(f"\nTOTAL  requests={total.num_requests}  failures={total.num_failures}  "
          f"RPS={total.current_rps:.1f}  "
          f"p95={total.get_response_time_percentile(0.95)}ms")
    print("="*60)
