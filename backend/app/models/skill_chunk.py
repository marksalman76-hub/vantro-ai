from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class SkillChunk(Base):
    __tablename__ = "skill_chunks"

    id = Column(Integer, primary_key=True)
    skill_name = Column(String(200), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True)  # JSON: list[float]
    char_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("skill_name", "chunk_index", name="uq_skill_chunk"),
    )
