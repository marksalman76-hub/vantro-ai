from datetime import datetime

from app.agents.agent_worker import _claim_job_for_execution, _positive_int_env
from app.models import Organization, Workspace
from app.models.agent_system import AgentJob

from conftest import make_user


def _workspace_id_for_user(db, user):
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    workspace = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    return workspace.id


def test_agent_worker_claim_is_atomic_for_parallel_workers(db):
    user, _token, _credits = make_user(db)
    workspace_id = _workspace_id_for_user(db, user)
    job = AgentJob(
        workspace_id=workspace_id,
        agent_id="social_media_content_agent",
        agent_name="Social Media Content Agent",
        status="pending",
        input_data="Create a launch post",
        credits_used=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()

    first_claim = _claim_job_for_execution(db, job.id)
    second_claim = _claim_job_for_execution(db, job.id)

    assert first_claim is not None
    assert first_claim.status == "running"
    assert second_claim is None


def test_agent_worker_claim_supports_approved_jobs(db):
    user, _token, _credits = make_user(db)
    workspace_id = _workspace_id_for_user(db, user)
    job = AgentJob(
        workspace_id=workspace_id,
        agent_id="ads_optimisation_agent",
        agent_name="Ads Optimisation Agent",
        status="approved",
        input_data="Review approved campaign changes",
        credits_used=4,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()

    claimed = _claim_job_for_execution(db, job.id)

    assert claimed is not None
    assert claimed.status == "running"


def test_positive_int_env_uses_default_for_invalid_values(monkeypatch):
    monkeypatch.setenv("AGENT_WORKER_MAX_CONCURRENT_JOBS", "not-a-number")

    assert _positive_int_env("AGENT_WORKER_MAX_CONCURRENT_JOBS", 3) == 3


def test_positive_int_env_reads_positive_values(monkeypatch):
    monkeypatch.setenv("AGENT_WORKER_MAX_CONCURRENT_JOBS", "25")

    assert _positive_int_env("AGENT_WORKER_MAX_CONCURRENT_JOBS", 3) == 25
