"""DB-01 missing FK indexes, DB-02 skill_chunks embedding_vec, DB-03 report FK constraints

Revision ID: 022
Revises: 021
Create Date: 2026-06-28
"""

import sqlalchemy as sa
from alembic import op

revision = "022"
down_revision = "021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── DB-01: Missing indexes on high-traffic FK columns ─────────────────────
    # Note: 017 already created idx_agent_jobs_workspace_id and idx_agent_jobs_status,
    # so we skip those here. All use IF NOT EXISTS for idempotency.
    for stmt in [
        "CREATE INDEX IF NOT EXISTS ix_api_keys_workspace_id ON api_keys (workspace_id)",
        "CREATE INDEX IF NOT EXISTS ix_workspace_integrations_workspace_id ON workspace_integrations (workspace_id)",
        "CREATE INDEX IF NOT EXISTS ix_workspaces_organization_id ON workspaces (organization_id)",
        "CREATE INDEX IF NOT EXISTS ix_organizations_owner_id ON organizations (owner_id)",
    ]:
        try:
            conn.execute(sa.text("SAVEPOINT idx_022_sp"))
            try:
                conn.execute(sa.text(stmt))
                conn.execute(sa.text("RELEASE SAVEPOINT idx_022_sp"))
            except Exception:
                conn.execute(sa.text("ROLLBACK TO SAVEPOINT idx_022_sp"))
        except Exception:
            pass

    # media_jobs — only if the table exists
    try:
        conn.execute(sa.text("SAVEPOINT media_022_sp"))
        try:
            result = conn.execute(
                sa.text("SELECT to_regclass('media_jobs')")
            ).scalar()
            if result:
                conn.execute(sa.text(
                    "CREATE INDEX IF NOT EXISTS ix_media_jobs_workspace_id ON media_jobs (workspace_id)"
                ))
            conn.execute(sa.text("RELEASE SAVEPOINT media_022_sp"))
        except Exception:
            conn.execute(sa.text("ROLLBACK TO SAVEPOINT media_022_sp"))
    except Exception:
        pass

    # ── DB-02: skill_chunks embedding_vec (pgvector, optional) ───────────────
    # Use SAVEPOINT so a missing pgvector extension doesn't abort the migration.
    try:
        conn.execute(sa.text("SAVEPOINT pgvector_022_sp"))
        try:
            conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.execute(sa.text(
                "ALTER TABLE skill_chunks ADD COLUMN IF NOT EXISTS embedding_vec vector(1536)"
            ))
            conn.execute(sa.text("RELEASE SAVEPOINT pgvector_022_sp"))
        except Exception:
            conn.execute(sa.text("ROLLBACK TO SAVEPOINT pgvector_022_sp"))
    except Exception:
        pass

    # ivfflat index — only if the column was successfully added
    try:
        conn.execute(sa.text("SAVEPOINT ivfflat_022_sp"))
        try:
            conn.execute(sa.text(
                "CREATE INDEX IF NOT EXISTS ix_skill_chunks_embedding_vec "
                "ON skill_chunks USING ivfflat (embedding_vec vector_cosine_ops) "
                "WITH (lists = 100)"
            ))
            conn.execute(sa.text("RELEASE SAVEPOINT ivfflat_022_sp"))
        except Exception:
            conn.execute(sa.text("ROLLBACK TO SAVEPOINT ivfflat_022_sp"))
    except Exception:
        pass

    # ── DB-03: FK constraints on workspace report tables ─────────────────────
    for constraint_sql, constraint_name, table in [
        (
            "ALTER TABLE workspace_report_settings "
            "ADD CONSTRAINT fk_wrs_workspace "
            "FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE",
            "fk_wrs_workspace",
            "workspace_report_settings",
        ),
        (
            "ALTER TABLE weekly_reports "
            "ADD CONSTRAINT fk_wr_workspace "
            "FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE",
            "fk_wr_workspace",
            "weekly_reports",
        ),
        (
            "ALTER TABLE report_feedback "
            "ADD CONSTRAINT fk_rf_workspace "
            "FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE",
            "fk_rf_workspace",
            "report_feedback",
        ),
    ]:
        try:
            # Check the table exists before attempting to add the constraint
            result = conn.execute(
                sa.text(f"SELECT to_regclass('{table}')")
            ).scalar()
            if result:
                conn.execute(sa.text("SAVEPOINT fk_022_sp"))
                try:
                    conn.execute(sa.text(constraint_sql))
                    conn.execute(sa.text("RELEASE SAVEPOINT fk_022_sp"))
                except Exception:
                    # Constraint likely already exists — silently skip
                    conn.execute(sa.text("ROLLBACK TO SAVEPOINT fk_022_sp"))
        except Exception:
            pass


def downgrade() -> None:
    conn = op.get_bind()

    # DB-03: drop FK constraints
    for constraint_name, table in [
        ("fk_rf_workspace", "report_feedback"),
        ("fk_wr_workspace", "weekly_reports"),
        ("fk_wrs_workspace", "workspace_report_settings"),
    ]:
        try:
            result = conn.execute(
                sa.text(f"SELECT to_regclass('{table}')")
            ).scalar()
            if result:
                conn.execute(sa.text(
                    f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint_name}"
                ))
        except Exception:
            pass

    # DB-02: drop ivfflat index and embedding_vec column
    try:
        conn.execute(sa.text(
            "DROP INDEX IF EXISTS ix_skill_chunks_embedding_vec"
        ))
    except Exception:
        pass
    try:
        conn.execute(sa.text(
            "ALTER TABLE skill_chunks DROP COLUMN IF EXISTS embedding_vec"
        ))
    except Exception:
        pass

    # DB-01: drop added indexes
    for stmt in [
        "DROP INDEX IF EXISTS ix_media_jobs_workspace_id",
        "DROP INDEX IF EXISTS ix_organizations_owner_id",
        "DROP INDEX IF EXISTS ix_workspaces_organization_id",
        "DROP INDEX IF EXISTS ix_workspace_integrations_workspace_id",
        "DROP INDEX IF EXISTS ix_api_keys_workspace_id",
    ]:
        try:
            conn.execute(sa.text(stmt))
        except Exception:
            pass
