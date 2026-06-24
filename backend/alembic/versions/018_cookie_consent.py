"""add cookie consent fields to users

Revision ID: 018
Revises: 016
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS cookie_consent BOOLEAN")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS cookie_consent_at TIMESTAMP")


def downgrade():
    op.drop_column("users", "cookie_consent_at")
    op.drop_column("users", "cookie_consent")
