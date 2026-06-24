"""add stripe_subscription_id and subscription_period_end to users

Revision ID: 015
Revises: 014
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("stripe_subscription_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("subscription_period_end", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("users", "subscription_period_end")
    op.drop_column("users", "stripe_subscription_id")
