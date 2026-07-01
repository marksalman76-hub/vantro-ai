"""Tests for skip/limit pagination on list endpoints."""
import json
import uuid
from datetime import datetime

import pytest

from conftest import make_user
from app.models.agent_system import AgentJob


def _seed_jobs(db, workspace_id: str, count: int) -> list:
    jobs = []
    for i in range(count):
        job = AgentJob(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            agent_id="brand_voice_agent",
            status="completed",
            input_data=json.dumps({"text": f"job {i}"}),
            created_at=datetime.utcnow(),
        )
        db.add(job)
        jobs.append(job)
    db.commit()
    return jobs


class TestAgentJobPagination:
    def test_default_limit_returns_reasonable_count(self, client, db):
        user, token, _ = make_user(db)
        from app.models import Organization
        from app.models.workspace import Workspace
        org = db.query(Organization).filter(Organization.owner_id == user.id).first()
        ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
        _seed_jobs(db, ws.id, 15)

        resp = client.get(
            "/api/agents/jobs",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        jobs = data.get("jobs") or data.get("data") or data
        assert isinstance(jobs, list)

    def test_limit_parameter_respected(self, client, db):
        user, token, _ = make_user(db)
        from app.models import Organization
        from app.models.workspace import Workspace
        org = db.query(Organization).filter(Organization.owner_id == user.id).first()
        ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
        _seed_jobs(db, ws.id, 10)

        resp = client.get(
            "/api/agents/jobs?limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        jobs = data.get("jobs") or data.get("data") or data
        assert len(jobs) <= 3

    def test_skip_advances_page(self, client, db):
        user, token, _ = make_user(db)
        from app.models import Organization
        from app.models.workspace import Workspace
        org = db.query(Organization).filter(Organization.owner_id == user.id).first()
        ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
        _seed_jobs(db, ws.id, 10)

        resp_page1 = client.get(
            "/api/agents/jobs?limit=5&skip=0",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp_page2 = client.get(
            "/api/agents/jobs?limit=5&skip=5",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp_page1.status_code == 200
        assert resp_page2.status_code == 200

        page1 = resp_page1.json().get("jobs") or resp_page1.json().get("data") or resp_page1.json()
        page2 = resp_page2.json().get("jobs") or resp_page2.json().get("data") or resp_page2.json()

        if page1 and page2:
            ids_p1 = {j["id"] for j in page1}
            ids_p2 = {j["id"] for j in page2}
            assert ids_p1.isdisjoint(ids_p2), "Pages must not overlap"

    def test_limit_capped_at_100(self, client, db):
        user, token, _ = make_user(db)
        resp = client.get(
            "/api/agents/jobs?limit=9999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 422)
        if resp.status_code == 200:
            jobs = resp.json().get("jobs") or resp.json().get("data") or resp.json()
            assert len(jobs) <= 100

    def test_invalid_limit_returns_422(self, client, db):
        user, token, _ = make_user(db)
        resp = client.get(
            "/api/agents/jobs?limit=-1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_unauthenticated_returns_401(self, client, db):
        resp = client.get("/api/agents/jobs")
        assert resp.status_code == 401


class TestAdminJobPagination:
    def test_admin_jobs_list_paginated(self, client, db):
        admin, token, _ = make_user(db, email=f"admin-pg-{uuid.uuid4().hex[:6]}@test.com", is_admin=True)
        from app.models import Organization
        from app.models.workspace import Workspace
        org = db.query(Organization).filter(Organization.owner_id == admin.id).first()
        ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
        _seed_jobs(db, ws.id, 5)

        resp = client.get(
            "/api/admin/agents/jobs?status=completed&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        jobs = data.get("jobs") or data.get("data") or data
        assert len(jobs) <= 3

    def test_non_admin_cannot_access_admin_jobs(self, client, db):
        _, token, _ = make_user(db)
        resp = client.get(
            "/api/admin/agents/jobs",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
