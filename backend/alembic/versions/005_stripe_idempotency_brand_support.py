"""Add Stripe webhook idempotency, brand_profile, and support_tickets

Revision ID: 005_stripe_idempotency_brand_support
Revises: 004_reconcile_and_agent_tables
Create Date: 2026-06-23
"""
from alembic import op

revision = "005_stripe_idempotency_brand_support"
down_revision = "004_reconcile_and_agent_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Stripe webhook idempotency — prevents double-processing on retry
    op.execute("""
        CREATE TABLE IF NOT EXISTS stripe_webhook_events (
            id           VARCHAR     PRIMARY KEY,
            event_type   VARCHAR     NOT NULL,
            processed_at TIMESTAMP   NOT NULL DEFAULT NOW()
        )
    """)

    # Brand profile stored server-side (replaces localStorage approach)
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS brand_profile JSONB")

    # Support tickets
    op.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id          VARCHAR     PRIMARY KEY,
            user_id     VARCHAR     NOT NULL REFERENCES users(id),
            email       VARCHAR     NOT NULL,
            ticket_type VARCHAR     NOT NULL,
            message     TEXT        NOT NULL,
            status      VARCHAR     NOT NULL DEFAULT 'open',
            created_at  TIMESTAMP   NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMP
        )
    """)

    op.execute("CREATE INDEX IF NOT EXISTS ix_support_tickets_user_id ON support_tickets (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_support_tickets_status  ON support_tickets (status)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS support_tickets")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS brand_profile")
    op.execute("DROP TABLE IF EXISTS stripe_webhook_events")
