"""Backfill Fernet encryption for PII columns (users.name, workspaces.business_context)

The EncryptedText TypeDecorator transparently encrypts new writes; this migration
backfills existing plaintext rows so the whole table is encrypted at rest.

Rows that already look like Fernet tokens (start with 'gAAAAA') are skipped to
make the migration safely re-runnable.

Revision ID: 019
Revises: 018
Create Date: 2026-06-24
"""

import logging

import sqlalchemy as sa
from alembic import op

revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None

logger = logging.getLogger(__name__)

_FERNET_PREFIX = "gAAAAA"  # all Fernet tokens start with this
_BATCH_SIZE = 100


def _already_encrypted(value: str) -> bool:
    """Return True if the stored value looks like a Fernet token (safe re-run guard)."""
    return value.startswith(_FERNET_PREFIX)


def upgrade():
    # Import here so Alembic env doesn't need the full app import chain at load time
    from app.services.encryption_service import encrypt  # noqa: PLC0415

    conn = op.get_bind()

    # ── Backfill users.name ────────────────────────────────────────────────────
    rows = conn.execute(
        sa.text("SELECT id, name FROM users WHERE name IS NOT NULL")
    ).fetchall()

    user_count = 0
    for i in range(0, len(rows), _BATCH_SIZE):
        batch = rows[i : i + _BATCH_SIZE]
        for row_id, name in batch:
            if _already_encrypted(name):
                continue
            encrypted = encrypt(name)
            conn.execute(
                sa.text("UPDATE users SET name = :enc WHERE id = :uid"),
                {"enc": encrypted, "uid": row_id},
            )
            user_count += 1

    logger.info("019 migration: encrypted %d users.name rows", user_count)

    # ── Backfill workspaces.business_context (only if column exists) ──────────
    inspector = sa.inspect(conn)
    ws_cols = [c["name"] for c in inspector.get_columns("workspaces")]
    ws_count = 0
    if "business_context" in ws_cols:
        rows = conn.execute(
            sa.text("SELECT id, business_context FROM workspaces WHERE business_context IS NOT NULL")
        ).fetchall()
        for i in range(0, len(rows), _BATCH_SIZE):
            batch = rows[i : i + _BATCH_SIZE]
            for row_id, ctx in batch:
                if _already_encrypted(ctx):
                    continue
                encrypted = encrypt(ctx)
                conn.execute(
                    sa.text("UPDATE workspaces SET business_context = :enc WHERE id = :wid"),
                    {"enc": encrypted, "wid": row_id},
                )
                ws_count += 1

    logger.info(
        "019 migration: encrypted %d workspaces.business_context rows", ws_count
    )


def downgrade():
    """Decrypt all rows back to plaintext.

    Only safe to run when the encryption key is still available.
    """
    from app.services.encryption_service import decrypt  # noqa: PLC0415

    conn = op.get_bind()

    # ── Restore users.name ────────────────────────────────────────────────────
    rows = conn.execute(
        sa.text("SELECT id, name FROM users WHERE name IS NOT NULL")
    ).fetchall()

    for row_id, name in rows:
        if not _already_encrypted(name):
            continue
        try:
            plaintext = decrypt(name)
        except Exception:
            continue  # leave unreadable rows alone
        conn.execute(
            sa.text("UPDATE users SET name = :pt WHERE id = :uid"),
            {"pt": plaintext, "uid": row_id},
        )

    # ── Restore workspaces.business_context ───────────────────────────────────
    rows = conn.execute(
        sa.text("SELECT id, business_context FROM workspaces WHERE business_context IS NOT NULL")
    ).fetchall()

    for row_id, ctx in rows:
        if not _already_encrypted(ctx):
            continue
        try:
            plaintext = decrypt(ctx)
        except Exception:
            continue
        conn.execute(
            sa.text("UPDATE workspaces SET business_context = :pt WHERE id = :wid"),
            {"pt": plaintext, "wid": row_id},
        )
