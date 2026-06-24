"""
SQLAlchemy TypeDecorator for transparent Fernet encryption at the column level.

Designed for PII fields that must be encrypted at rest but are NOT used in
WHERE-clause lookups (e.g. name, business_context).

DO NOT apply to columns used in filter()/WHERE clauses (email, reset_token,
stripe_customer_id) — encrypted ciphertext would never match a plaintext query.

Handles legacy unencrypted rows gracefully: if decryption fails the raw stored
value is returned as-is so existing rows continue to work before backfilling.
"""

from sqlalchemy import TypeDecorator, Text

from app.services.encryption_service import encrypt, decrypt


class EncryptedText(TypeDecorator):
    """Transparent Fernet encryption for TEXT columns storing PII."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Encrypt on write. None is stored as NULL."""
        if value is None:
            return None
        return encrypt(str(value))

    def process_result_value(self, value, dialect):
        """Decrypt on read. Falls back to raw value for legacy unencrypted rows."""
        if value is None:
            return None
        try:
            return decrypt(value)
        except Exception:
            # Return raw plaintext for rows that pre-date encryption (before migration 019)
            return value
