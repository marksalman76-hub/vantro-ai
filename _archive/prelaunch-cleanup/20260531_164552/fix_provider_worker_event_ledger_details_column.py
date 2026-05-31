import os
import psycopg
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL")

env_file = Path(".env.local")
if not DATABASE_URL and env_file.exists():
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("DATABASE_URL = os.getenv('DATABASE_URL', '')=", 1)[1].strip().strip('"').strip("'")
            break

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found.")

SQL = """
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'provider_worker_event_ledger'
          AND column_name = 'details'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'provider_worker_event_ledger'
          AND column_name = 'details_json'
    )
    THEN
        ALTER TABLE provider_worker_event_ledger
        RENAME COLUMN details TO details_json;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'provider_worker_event_ledger'
          AND column_name = 'details_json'
    )
    THEN
        ALTER TABLE provider_worker_event_ledger
        ADD COLUMN details_json JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;
"""

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(SQL)
    conn.commit()

print("PROVIDER_WORKER_EVENT_LEDGER_DETAILS_COLUMN_FIXED")