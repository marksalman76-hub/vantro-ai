"""Add skill_chunks table with pgvector for RAG

Revision ID: 011
Revises: 010_composio_workspace_integration
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade():
    # pgvector is optional — use SAVEPOINT so a missing extension doesn't abort the migration
    connection = op.get_bind()
    connection.execute(sa.text("SAVEPOINT pgvector_sp"))
    try:
        connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.execute(sa.text("RELEASE SAVEPOINT pgvector_sp"))
    except Exception:
        connection.execute(sa.text("ROLLBACK TO SAVEPOINT pgvector_sp"))
    inspector = sa.inspect(connection)
    if "skill_chunks" not in inspector.get_table_names():
        op.create_table(
            "skill_chunks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("skill_name", sa.String(200), nullable=False),
            sa.Column("chunk_index", sa.Integer(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("embedding", sa.Text(), nullable=True),
            sa.Column("char_count", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        )
        op.create_index("ix_skill_chunks_skill_name", "skill_chunks", ["skill_name"])
        op.create_unique_constraint("uq_skill_chunk", "skill_chunks", ["skill_name", "chunk_index"])


def downgrade():
    op.drop_table("skill_chunks")
    op.execute("DROP EXTENSION IF EXISTS vector")
