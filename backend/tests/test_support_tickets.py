"""Integration tests for support ticket API."""
import pytest
from fastapi import status


@pytest.mark.unit
class TestSupportTickets:
    def test_create_ticket_unauthenticated(self, client):
        resp = client.post("/api/support/tickets", json={
            "ticket_type": "general",
            "subject": "Help",
            "detail": "Need help with my account",
        })
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_ticket_authenticated(self, client, authenticated_client):
        resp = authenticated_client.post("/api/support/tickets", json={
            "ticket_type": "general",
            "subject": "Test ticket",
            "detail": "This is a test support request.",
        })
        # May 201 or 200 depending on implementation; either means success
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        body = resp.json()
        assert "ticket_id" in body
        assert body.get("status") == "open"

    def test_create_ticket_missing_fields(self, client, authenticated_client):
        resp = authenticated_client.post("/api/support/tickets", json={
            "ticket_type": "general",
        })
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_own_tickets(self, client, authenticated_client):
        authenticated_client.post("/api/support/tickets", json={
            "ticket_type": "billing",
            "subject": "Invoice question",
            "detail": "Please help with my invoice.",
        })
        resp = authenticated_client.get("/api/support/tickets")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "tickets" in body
        assert isinstance(body["tickets"], list)
        assert len(body["tickets"]) >= 1

    def test_list_tickets_unauthenticated(self, client):
        resp = client.get("/api/support/tickets")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
