"""Add external_job_id to media_jobs, reset_token fields to users

Revision ID: 002_add_heygen_and_password_reset
Revises: 001_initial_schema
Create Date: 2026-06-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "002_add_heygen_and_password_reset"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use ADD COLUMN IF NOT EXISTS (PostgreSQL 9.6+) so re-running is safe
    op.execute("ALTER TABLE media_jobs ADD COLUMN IF NOT EXISTS external_job_id VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP")


def downgrade() -> None:
    op.drop_column("users", "reset_token_expires")
    op.drop_column("users", "reset_token")
    op.drop_column("media_jobs", "external_job_id")
