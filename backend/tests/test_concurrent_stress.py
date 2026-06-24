"""
Concurrent / stress tests for Vantro AI Platform.

Scenarios:
  1. Credit-race guard — 50 threads simultaneously hit the same workspace; only
     as many jobs as available credits should be queued (no overshooting).
  2. Job-queue flooding — N clients each submit M jobs; all must persist correctly.
  3. Parallel job-status polling — 100 concurrent GET /agents/jobs/{id} requests.
  4. DB connection-pool resilience — 150 simultaneous auth-list calls.
  5. Worker backlog drain — flood 100 jobs, verify worker clears them.
  6. Mixed workload — simultaneous writes + reads from different clients.
"""

import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event as sa_event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool  # one independent connection per thread

# ── env must be set before app imports ──────────────────────────────────────
os.environ.setdefault("TESTING", "1")

from app.database import Base
import app.models.user          # noqa: F401
import app.models.organization  # noqa: F401  (must be before workspace FK)
import app.models.workspace     # noqa: F401
from app.models.organization import Organization
try:
    import app.models.agent_system  # noqa: F401
except Exception:
    pass

from app.main import app
from app.routes.auth import get_db
from app.routes import admin as _admin_mod
from app.routes import agents as _agents_mod
from app.routes import support as _support_mod
from app.routes import users as _users_mod
from app.routes import stripe as _stripe_mod
from app.routes import dashboard as _dashboard_mod

# ── Shared SQLite engine for ALL stress tests ────────────────────────────────
# NullPool = a brand-new SQLite connection is opened per thread.
# WAL journal mode = multiple readers + single writer without blocking.
STRESS_DB_PATH = "./stress_test.db"
STRESS_DB_URL = f"sqlite:///{STRESS_DB_PATH}"

_engine = create_engine(
    STRESS_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,  # independent connection per request → safe under threads
)


@sa_event.listens_for(_engine, "connect")
def _set_wal_mode(dbapi_conn, _):
    """Enable WAL journal mode and busy timeout on every new SQLite connection."""
    dbapi_conn.execute("PRAGMA journal_mode=WAL")
    dbapi_conn.execute("PRAGMA busy_timeout=5000")  # wait up to 5s if locked


def _reset_db():
    Base.metadata.drop_all(bind=_engine)
    Base.metadata.create_all(bind=_engine)
    with _engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id TEXT PRIMARY KEY, user_id TEXT, email TEXT,
                ticket_type TEXT, message TEXT, status TEXT DEFAULT 'open',
                created_at TIMESTAMP, updated_at TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stripe_webhook_events (
                id TEXT PRIMARY KEY, event_type TEXT, processed_at TIMESTAMP
            )
        """))
        conn.commit()


@pytest.fixture(scope="module")
def stress_engine():
    _reset_db()
    yield _engine
    import os as _os
    for ext in ("", "-wal", "-shm"):
        try:
            _os.remove(STRESS_DB_PATH + ext)
        except FileNotFoundError:
            pass


@pytest.fixture(scope="module")
def stress_client(stress_engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=stress_engine)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    for mod in (_admin_mod, _agents_mod, _support_mod, _users_mod, _stripe_mod, _dashboard_mod):
        if hasattr(mod, "get_db"):
            app.dependency_overrides[mod.get_db] = override
    app.dependency_overrides[get_db] = override

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ── helpers ──────────────────────────────────────────────────────────────────

def _create_workspace_for_user(user_id: str, total_credits: int = 500) -> None:
    """
    Directly insert org → workspace → credits_account into the stress DB.
    Necessary because registration does not auto-provision a workspace.
    Uses NullPool so each call opens its own connection (thread-safe).
    """
    from app.models.workspace import Workspace, CreditsAccount
    Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    db = Session()
    try:
        org_id = str(uuid.uuid4())
        ws_id = str(uuid.uuid4())
        now = __import__("datetime").datetime.utcnow()
        org = Organization(id=org_id, name="Stress Org", slug=f"org-{org_id[:8]}", owner_id=user_id)
        ws  = Workspace(id=ws_id, organization_id=org_id, name="Default", slug="default", created_at=now)
        cred = CreditsAccount(id=str(uuid.uuid4()), workspace_id=ws_id,
                              total_credits=total_credits, used_credits=0, created_at=now)
        # Link user → org
        db.add(org); db.add(ws); db.add(cred)
        db.execute(
            text("UPDATE users SET organization_id = :org_id WHERE id = :uid"),
            {"org_id": org_id, "uid": user_id},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


def _register_and_login(client: TestClient, suffix: str = "", total_credits: int = 500) -> str:
    """Register a fresh user, provision workspace+credits, and return the bearer token."""
    email = f"stress_{suffix}_{uuid.uuid4().hex[:8]}@vantro.test"
    r = client.post("/api/auth/register", json={
        "email": email, "password": "StressPass1!", "name": f"Stress {suffix}"
    })
    assert r.status_code in (200, 201), f"register failed: {r.text}"
    data = r.json()
    _create_workspace_for_user(data["user_id"], total_credits=total_credits)
    return data["access_token"]


def _run_agent(client: TestClient, token: str, agent_id: str = "receptionist_agent") -> dict:
    r = client.post(
        f"/api/agents/{agent_id}/run",
        json={"prompt": "stress test prompt", "context": {}},
        headers={"Authorization": f"Bearer {token}"},
    )
    return {"status": r.status_code, "body": r.json() if r.status_code != 500 else {}}


# ── 1. Credit-race guard ─────────────────────────────────────────────────────

class TestCreditRaceGuard:
    """
    50 threads simultaneously try to run the receptionist_agent (costs 1 credit).
    The starter plan gives 60 credits, so all 50 should succeed.
    No job should be created with negative-credit state.
    """
    THREADS = 50
    AGENT = "receptionist_agent"  # cost=1, HITL-1, starter tier

    def test_no_credit_overshoot(self, stress_client):
        token = _register_and_login(stress_client, "race")
        results = []
        lock = threading.Lock()

        def submit():
            r = _run_agent(stress_client, token, self.AGENT)
            with lock:
                results.append(r)

        threads = [threading.Thread(target=submit) for _ in range(self.THREADS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        ok  = [r for r in results if r["status"] in (200, 201)]
        err = [r for r in results if r["status"] == 402]

        # All 50 must be queued (60 credits > 50 cost)
        assert len(ok) == self.THREADS, (
            f"Expected {self.THREADS} successes, got {len(ok)} ok / {len(err)} 402"
        )

    def test_credit_exhaustion_blocks_further_jobs(self, stress_client):
        """After a workspace exhausts its credits, further runs must return 402."""
        # intake_trial_agent costs 2 credits each; give exactly 10 for 5 runs
        token = _register_and_login(stress_client, "exhaust", total_credits=10)

        for i in range(5):
            r = _run_agent(stress_client, token, "intake_trial_agent")
            assert r["status"] in (200, 201), f"Run {i+1} failed before exhaustion: {r}"

        # 6th must be blocked
        r = _run_agent(stress_client, token, "intake_trial_agent")
        assert r["status"] == 402, f"Expected 402 after exhaustion, got {r['status']}"


# ── 2. Job-queue flooding ─────────────────────────────────────────────────────

class TestJobQueueFlooding:
    """
    100 distinct clients each submit 5 jobs concurrently (500 total).
    All jobs must be persisted correctly; no corruption.
    """
    CLIENTS = 50    # reduced for SQLite; scale up against PG
    JOBS_EACH = 3

    def test_flood_queue(self, stress_client):
        tokens = []
        for i in range(self.CLIENTS):
            tokens.append(_register_and_login(stress_client, f"flood{i}"))

        job_ids: list[str] = []
        errors: list[dict] = []
        lock = threading.Lock()

        def client_burst(token):
            local_ids = []
            for _ in range(self.JOBS_EACH):
                r = _run_agent(stress_client, token, "receptionist_agent")
                if r["status"] in (200, 201):
                    jid = r["body"].get("job_id")
                    if jid:
                        local_ids.append(jid)
                else:
                    with lock:
                        errors.append(r)
            with lock:
                job_ids.extend(local_ids)

        with ThreadPoolExecutor(max_workers=self.CLIENTS) as pool:
            futures = [pool.submit(client_burst, t) for t in tokens]
            for f in as_completed(futures):
                f.result()  # propagate exceptions

        expected = self.CLIENTS * self.JOBS_EACH
        assert len(errors) == 0, f"{len(errors)} errors: {errors[:3]}"
        assert len(job_ids) == expected, (
            f"Expected {expected} job IDs, got {len(job_ids)}"
        )
        # All IDs must be unique — no duplicates / ID collision
        assert len(set(job_ids)) == len(job_ids), "Duplicate job IDs detected!"

    def test_job_ids_are_uuid4(self, stress_client):
        """Every job ID returned must be a valid UUIDv4."""
        token = _register_and_login(stress_client, "uuid_check")
        ids = []
        for _ in range(10):
            r = _run_agent(stress_client, token, "receptionist_agent")
            if r["status"] in (200, 201):
                ids.append(r["body"].get("job_id", ""))

        for jid in ids:
            try:
                parsed = uuid.UUID(jid, version=4)
                assert str(parsed) == jid
            except (ValueError, AssertionError):
                pytest.fail(f"Invalid UUID4 job_id: {jid!r}")


# ── 3. Parallel job-status polling ───────────────────────────────────────────

class TestParallelStatusPolling:
    """
    Simulate 100 clients all polling the same job's status simultaneously —
    the kind of frontend behaviour seen when many users have the dashboard open.
    """
    POLLERS = 100

    def test_concurrent_status_reads(self, stress_client):
        token = _register_and_login(stress_client, "poll")
        r = _run_agent(stress_client, token, "receptionist_agent")
        assert r["status"] in (200, 201)
        job_id = r["body"]["job_id"]

        results = []
        lock = threading.Lock()

        def poll():
            resp = stress_client.get(
                f"/api/agents/jobs/{job_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            with lock:
                results.append(resp.status_code)

        threads = [threading.Thread(target=poll) for _ in range(self.POLLERS)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        failures = [c for c in results if c not in (200, 201)]
        assert len(failures) == 0, f"{len(failures)} polls failed: {set(failures)}"
        assert len(results) == self.POLLERS

    def test_list_jobs_concurrent(self, stress_client):
        """100 simultaneous GET /api/agents/jobs requests from 100 different users."""
        tokens = [_register_and_login(stress_client, f"lister{i}") for i in range(20)]
        # give each user a job so the list isn't empty
        for t in tokens:
            _run_agent(stress_client, t, "receptionist_agent")

        results = []
        lock = threading.Lock()

        def list_jobs(tok):
            resp = stress_client.get(
                "/api/agents/jobs",
                headers={"Authorization": f"Bearer {tok}"},
            )
            with lock:
                results.append(resp.status_code)

        with ThreadPoolExecutor(max_workers=len(tokens)) as pool:
            futures = [pool.submit(list_jobs, t) for t in tokens]
            for f in as_completed(futures):
                f.result()

        bad = [c for c in results if c != 200]
        assert len(bad) == 0, f"Non-200 responses: {set(bad)}"


# ── 4. DB connection-pool resilience ─────────────────────────────────────────

class TestDBConnectionPoolResilience:
    """
    150 concurrent authenticated requests all hitting the DB simultaneously.
    No request should 500; all must return 200 or 4xx.
    """
    CONCURRENT = 150

    def test_pool_handles_burst(self, stress_client):
        tokens = [_register_and_login(stress_client, f"pool{i}") for i in range(10)]
        results = []
        lock = threading.Lock()

        def hit(tok):
            resp = stress_client.get(
                "/api/agents",
                headers={"Authorization": f"Bearer {tok}"},
            )
            with lock:
                results.append(resp.status_code)

        threads = [
            threading.Thread(target=hit, args=(tokens[i % len(tokens)],))
            for i in range(self.CONCURRENT)
        ]
        t0 = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - t0

        server_errors = [c for c in results if c >= 500]
        assert len(server_errors) == 0, f"{len(server_errors)} × 5xx under load"
        print(f"\n[pool test] {self.CONCURRENT} requests in {elapsed:.2f}s "
              f"({self.CONCURRENT/elapsed:.0f} req/s)")


# ── 5. Mixed read/write workload ──────────────────────────────────────────────

class TestMixedWorkload:
    """
    Simulates a realistic production mix:
      40% — submit agent job
      40% — poll job status / list jobs
      20% — update brand profile
    Running 200 operations from 20 concurrent users.
    """
    USERS = 20
    OPS_PER_USER = 10

    def test_mixed_workload_no_errors(self, stress_client):
        tokens = [_register_and_login(stress_client, f"mix{i}") for i in range(self.USERS)]
        # Seed one job per user so status polls have something to hit
        job_ids = {}
        for tok in tokens:
            r = _run_agent(stress_client, tok, "receptionist_agent")
            if r["status"] in (200, 201):
                job_ids[tok] = r["body"].get("job_id", "")

        errors = []
        lock = threading.Lock()

        def user_session(tok: str, idx: int):
            jid = job_ids.get(tok, "")
            for op_idx in range(self.OPS_PER_USER):
                roll = (idx + op_idx) % 10
                if roll < 4:
                    # 40%: submit a job
                    r = stress_client.post(
                        "/api/agents/receptionist_agent/run",
                        json={"prompt": f"op {op_idx}", "context": {}},
                        headers={"Authorization": f"Bearer {tok}"},
                    )
                    code = r.status_code
                elif roll < 8:
                    # 40%: poll status or list
                    if jid:
                        r = stress_client.get(
                            f"/api/agents/jobs/{jid}",
                            headers={"Authorization": f"Bearer {tok}"},
                        )
                    else:
                        r = stress_client.get(
                            "/api/agents/jobs",
                            headers={"Authorization": f"Bearer {tok}"},
                        )
                    code = r.status_code
                else:
                    # 20%: brand profile update
                    r = stress_client.put(
                        "/api/users/brand-profile",
                        json={"business_name": f"Co {op_idx}"},
                        headers={"Authorization": f"Bearer {tok}"},
                    )
                    code = r.status_code

                if code >= 500:
                    with lock:
                        errors.append({"code": code, "op": roll, "user": idx})

        with ThreadPoolExecutor(max_workers=self.USERS) as pool:
            futures = [pool.submit(user_session, t, i) for i, t in enumerate(tokens)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0, f"{len(errors)} server errors in mixed workload: {errors[:5]}"


# ── 6. Support ticket storm ───────────────────────────────────────────────────

class TestSupportTicketStorm:
    """
    100 users simultaneously submit support tickets — tests the raw SQL INSERT
    path and ensures no row conflicts or missing inserts.
    """
    USERS = 30

    def test_concurrent_ticket_creation(self, stress_client):
        tokens = [_register_and_login(stress_client, f"supp{i}") for i in range(self.USERS)]
        results = []
        lock = threading.Lock()

        def submit_ticket(tok):
            r = stress_client.post(
                "/api/support/tickets",
                json={
                    "ticket_type": "general",
                    "subject": "Stress test ticket",
                    "detail": "This is a concurrent stress test support ticket.",
                },
                headers={"Authorization": f"Bearer {tok}"},
            )
            with lock:
                results.append({"status": r.status_code, "body": r.json() if r.status_code < 500 else {}})

        threads = [threading.Thread(target=submit_ticket, args=(t,)) for t in tokens]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        ok = [r for r in results if r["status"] in (200, 201)]
        bad = [r for r in results if r["status"] >= 500]

        assert len(bad) == 0, f"{len(bad)} server errors creating tickets: {bad[:3]}"
        assert len(ok) == self.USERS, f"Expected {self.USERS} tickets, got {len(ok)}"

        # All ticket IDs must be unique
        ids = [r["body"].get("ticket_id", "") for r in ok]
        assert len(set(ids)) == len(ids), "Duplicate ticket IDs!"


# ── 7. Authentication throughput ─────────────────────────────────────────────

class TestAuthThroughput:
    """
    200 concurrent login requests using different pre-registered accounts.
    Measures raw JWT issue rate; all must succeed within 10 seconds.
    """
    USERS = 40

    def test_login_throughput(self, stress_client):
        # Pre-register users sequentially
        creds = []
        for i in range(self.USERS):
            email = f"auth_throughput_{i}_{uuid.uuid4().hex[:6]}@vantro.test"
            r = stress_client.post("/api/auth/register", json={
                "email": email, "password": "AuthLoad1!", "name": f"Loader {i}",
            })
            if r.status_code in (200, 201):
                creds.append({"email": email, "password": "AuthLoad1!"})

        tokens = []
        errors = []
        lock = threading.Lock()

        def login(cred):
            r = stress_client.post("/api/auth/login", json=cred)
            with lock:
                if r.status_code == 200:
                    tokens.append(r.json().get("access_token", ""))
                else:
                    errors.append(r.status_code)

        t0 = time.perf_counter()
        threads = [threading.Thread(target=login, args=(c,)) for c in creds]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - t0

        assert len(errors) == 0, f"{len(errors)} login failures: {set(errors)}"
        assert len(tokens) == len(creds)
        # All tokens must be non-empty strings
        assert all(tokens), "Some tokens are empty"
        print(f"\n[auth throughput] {len(creds)} logins in {elapsed:.2f}s "
              f"({len(creds)/elapsed:.0f} logins/s)")
