"""
Encryption service for workspace integration credentials.

Uses Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256).
Key sourced from INTEGRATION_ENCRYPTION_KEY env var; falls back to
a key derived from SECRET_KEY so the app works without extra config.

SECURITY RULES (enforced here, never elsewhere):
- encrypt() is the only entry point for storing a credential.
- decrypt() is only called internally for connection testing — the raw
  value is NEVER returned to any API response, logged, or serialised.
- Callers must use redacted_meta() to build safe API responses.
"""

import base64
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

_fernet = None


def _get_fernet():
    global _fernet
    if _fernet is not None:
        return _fernet

    from cryptography.fernet import Fernet

    raw_key = os.getenv("INTEGRATION_ENCRYPTION_KEY", "").strip()
    if raw_key:
        # Expect a URL-safe base64 32-byte Fernet key
        try:
            _fernet = Fernet(raw_key.encode())
            return _fernet
        except Exception:
            logger.warning("INTEGRATION_ENCRYPTION_KEY is set but invalid — falling back to derived key")

    # Derive a stable Fernet key from SECRET_KEY so the app always works
    secret = os.getenv("SECRET_KEY", "vantro-default-secret-change-in-production")
    derived = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    _fernet = Fernet(derived)
    return _fernet


def encrypt(plaintext: str) -> str:
    """Encrypt a credential. Returns URL-safe base64 ciphertext string."""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a credential. For internal testing only — never expose to API."""
    f = _get_fernet()
    return f.decrypt(ciphertext.encode()).decode()


def redacted_meta(plaintext_value: str) -> dict:
    """
    Return safe metadata about a credential value.
    Never includes the actual value.
    """
    length = len(plaintext_value)
    return {
        "present": True,
        "length": length,
        "redacted": f"{'*' * min(length, 6)}…",
        "prefix": plaintext_value[:4] + "…" if length > 4 else "****",
    }
