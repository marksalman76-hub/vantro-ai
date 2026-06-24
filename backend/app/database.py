import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from app.config import get_config

DATABASE_URL = get_config(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/multi_industrial_dev",
)

# Optional read replica URL — set DATABASE_REPLICA_URL in ECS task environment
# to the rds_replica_endpoint Terraform output. Falls back to primary when unset.
DATABASE_REPLICA_URL = os.getenv("DATABASE_REPLICA_URL", DATABASE_URL)

_POOL_KWARGS = dict(
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
)

engine = create_engine(DATABASE_URL, **_POOL_KWARGS)

# Read replica engine — smaller pool since it only handles SELECT workloads
_replica_pool_kwargs = {**_POOL_KWARGS, "pool_size": 3, "max_overflow": 5}
replica_engine = create_engine(DATABASE_REPLICA_URL, **_replica_pool_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ReadSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=replica_engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    """Yield a read-only session routed to the RDS read replica.

    Use this for GET list endpoints that don't need the primary's write-ahead log.
    Falls back to the primary if DATABASE_REPLICA_URL is not configured.
    """
    db = ReadSessionLocal()
    try:
        yield db
    finally:
        db.close()
