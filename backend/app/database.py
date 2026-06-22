import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Jessica2007!@localhost:5432/multi_industrial_dev"
)

# Connection pool sizing:
# pool_size=5  → base connections per process kept alive
# max_overflow=10 → burst headroom above pool_size (max 15 total per process)
# pool_timeout=30 → seconds to wait for a free connection before raising
# pool_recycle=1800 → recycle connections every 30 min (avoids stale conn errors from RDS idle timeouts)
# pool_pre_ping=True → test each connection before use (drops silently-dead connections)
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    # Echo only in local dev; production keeps logs clean
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
