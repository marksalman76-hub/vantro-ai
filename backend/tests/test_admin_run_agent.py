import json

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

    workspace = db.query(Workspace).filter(Workspace.organization_id == admin.organization_id).first()
    job = db.query(AgentJob).filter(AgentJob.id == payload["job_id"]).first()
    db.refresh(credits)

    assert job is not None
    assert job.workspace_id == workspace.id
    assert job.credits_used == 0
    assert credits.used_credits == 0

    input_data = json.loads(job.input_data)
    route = input_data["context"]["creative_provider_route"]
    assert route["video"]["provider"] == "higgsfield"
    assert route["video"]["model"] == "Kling 3.0 Turbo"
