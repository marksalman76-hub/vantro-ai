"""Tests for refresh token issuance, rotation, and revocation."""
import hashlib
import uuid
from datetime import datetime, timedelta

import pytest

from conftest import make_user
from app.models.refresh_token import RefreshToken


def _make_refresh_token(db, user_id: str, *, days=7, revoked=False) -> tuple[str, RefreshToken]:
    import secrets
    opaque = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(opaque.encode()).hexdigest()
    rt = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=days),
        revoked_at=datetime.utcnow() if revoked else None,
    )
    db.add(rt)
    db.commit()
    return opaque, rt


class TestRefreshTokenIssuance:
    def test_login_sets_refresh_cookie(self, client, db):
        user, _, _ = make_user(db)
        resp = client.post("/api/auth/login", json={"email": user.email, "password": "Test1234!"})
        assert resp.status_code == 200
        assert "refresh_token" in resp.cookies

    def test_login_sets_access_cookie(self, client, db):
        user, _, _ = make_user(db)
        resp = client.post("/api/auth/login", json={"email": user.email, "password": "Test1234!"})
        assert resp.status_code == 200
        assert "access_token" in resp.cookies

    def test_register_sets_refresh_cookie(self, client, db):
        resp = client.post("/api/auth/register", json={
            "email": f"new-{uuid.uuid4().hex[:6]}@test.com",
            "password": "Test1234!",
            "name": "New User",
        })
        assert resp.status_code == 201
        assert "refresh_token" in resp.cookies

    def test_refresh_token_stored_hashed(self, client, db):
        user, _, _ = make_user(db)
        resp = client.post("/api/auth/login", json={"email": user.email, "password": "Test1234!"})
        opaque = resp.cookies["refresh_token"]
        expected_hash = hashlib.sha256(opaque.encode()).hexdigest()
        stored = db.query(RefreshToken).filter(RefreshToken.token_hash == expected_hash).first()
        assert stored is not None
        assert stored.user_id == user.id


class TestRefreshTokenRotation:
    def test_refresh_issues_new_access_token(self, client, db):
        user, _, _ = make_user(db)
        login_resp = client.post("/api/auth/login", json={"email": user.email, "password": "Test1234!"})
        old_access = login_resp.json()["access_token"]

        refresh_resp = client.post("/api/auth/refresh")
        assert refresh_resp.status_code == 200
        new_access = refresh_resp.json()["access_token"]
        assert new_access != old_access

    def test_refresh_revokes_old_refresh_token(self, client, db):
        user, _, _ = make_user(db)
        login_resp = client.post("/api/auth/login", json={"email": user.email, "password": "Test1234!"})
        old_opaque = login_resp.cookies["refresh_token"]
        old_hash = hashlib.sha256(old_opaque.encode()).hexdigest()

        client.post("/api/auth/refresh")

        old_rt = db.query(RefreshToken).filter(RefreshToken.token_hash == old_hash).first()
        db.refresh(old_rt)
        assert old_rt.revoked_at is not None

    def test_refresh_issues_new_refresh_cookie(self, client, db):
        user, _, _ = make_user(db)
        login_resp = client.post("/api/auth/login", json={"email": user.email, "password": "Test1234!"})
        old_opaque = login_resp.cookies["refresh_token"]

        refresh_resp = client.post("/api/auth/refresh")
        new_opaque = refresh_resp.cookies.get("refresh_token")
        assert new_opaque is not None
        assert new_opaque != old_opaque

    def test_revoked_refresh_token_rejected(self, client, db):
        user, _, _ = make_user(db)
        opaque, _ = _make_refresh_token(db, user.id, revoked=True)
        client.cookies.set("refresh_token", opaque)
        resp = client.post("/api/auth/refresh")
        assert resp.status_code == 401

    def test_expired_refresh_token_rejected(self, client, db):
        user, _, _ = make_user(db)
        opaque, _ = _make_refresh_token(db, user.id, days=-1)
        client.cookies.set("refresh_token", opaque)
        resp = client.post("/api/auth/refresh")
        assert resp.status_code == 401

    def test_missing_refresh_token_rejected(self, client, db):
        resp = client.post("/api/auth/refresh")
        assert resp.status_code == 401


class TestLogoutRevocation:
    def test_logout_revokes_refresh_token(self, client, db):
        user, _, _ = make_user(db)
        login_resp = client.post("/api/auth/login", json={"email": user.email, "password": "Test1234!"})
        opaque = login_resp.cookies["refresh_token"]
        token_hash = hashlib.sha256(opaque.encode()).hexdigest()

        client.post("/api/auth/logout")

        rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        db.refresh(rt)
        assert rt.revoked_at is not None

    def test_refresh_after_logout_fails(self, client, db):
        user, _, _ = make_user(db)
        client.post("/api/auth/login", json={"email": user.email, "password": "Test1234!"})
        client.post("/api/auth/logout")
        resp = client.post("/api/auth/refresh")
        assert resp.status_code == 401
