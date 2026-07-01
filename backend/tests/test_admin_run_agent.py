import json

from app.agents.agent_worker import (
    _job_uses_owner_admin_unlimited_billing,
    _resolve_billable_credit_cost,
)
from app.models.agent_system import AgentJob
from app.models.workspace import Workspace
from conftest import make_user


def test_admin_run_agent_uses_admin_organization_workspace(client, db):
    admin, token, credits = make_user(db, email="admin@example.com", is_admin=True)

    response = client.post(
        "/api/admin/agents/ugc_media_agent/run",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "prompt": "Create a short product demo video.",
            "context": {
                "media_request": {
                    "type": "product_demo",
                    "video_quality": "720p",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_id"] == "ugc_media_agent"
    assert payload["job_id"]

    db.expire_all()
    workspace = db.query(Workspace).filter(Workspace.organization_id == admin.organization_id).first()
    job = db.query(AgentJob).filter(AgentJob.id == payload["job_id"]).first()
    db.refresh(credits)

    assert job is not None
    assert job.workspace_id == workspace.id
    assert job.credits_used == 0
    assert credits.used_credits == 0

    input_data = json.loads(job.input_data)
    route = input_data["context"]["creative_provider_route"]
    assert route["video"]["provider"] == "kling"
    assert route["video"]["model"] == "Kling 3.0 Turbo"
    assert input_data["context"]["billing_mode"] == "owner_admin_unlimited"
    assert input_data["context"]["package_tier"] == "enterprise"
    assert input_data["context"]["credits_unlimited"] is True
    assert _job_uses_owner_admin_unlimited_billing(job) is True
    assert _resolve_billable_credit_cost(
        actual_credits=42,
        pre_committed=job.credits_used,
        owner_admin_unlimited=True,
    ) == 0


def test_admin_run_agent_uses_requested_creative_identity_for_premium_route(client, db):
    admin, token, credits = make_user(db, email="creative-admin@example.com", is_admin=True)

    response = client.post(
        "/api/admin/agents/ugc_creative_agent/run",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "prompt": "Create a cinematic 4K product launch video.",
            "context": {
                "media_request": {
                    "type": "product_demo",
                    "video_quality": "4K",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_id"] == "ugc_media_agent"
    assert payload["job_id"]

    db.expire_all()
    workspace = db.query(Workspace).filter(Workspace.organization_id == admin.organization_id).first()
    job = db.query(AgentJob).filter(AgentJob.id == payload["job_id"]).first()
    db.refresh(credits)

    assert job is not None
    assert job.workspace_id == workspace.id
    assert job.credits_used == 0
    assert credits.used_credits == 0

    input_data = json.loads(job.input_data)
    route = input_data["context"]["creative_provider_route"]
    assert route["canonical_agent_id"] == "ugc_creative_agent"
    assert route["video"]["provider"] == "kling"
    assert route["video"]["model"] == "Cinema Studio 4K"
