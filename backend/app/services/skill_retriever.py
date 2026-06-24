"""
Skill retriever: given a task description, finds the most relevant
skill chunks via cosine similarity and returns a formatted context block.
"""
import json
import math
import os
from typing import Optional
from sqlalchemy.orm import Session


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _embed_text(text: str) -> Optional[list[float]]:
    try:
        import openai
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        resp = client.embeddings.create(model="text-embedding-3-small", input=[text[:2000]])
        return resp.data[0].embedding
    except Exception:
        return None


def retrieve_relevant_skills(
    db: Session,
    task_description: str,
    top_k: int = 3,
    min_similarity: float = 0.45,
) -> Optional[str]:
    """
    Embed task_description, find top-k skill chunks by cosine similarity.
    Returns formatted string block or None if no relevant chunks found.
    Never raises — failure is silent (agents work without RAG).
    """
    try:
        from app.models.skill_chunk import SkillChunk

        # Check if any chunks exist
        count = db.query(SkillChunk).count()
        if count == 0:
            return None

        query_emb = _embed_text(task_description)
        if not query_emb:
            return None

        # Load all chunks (acceptable at < 5000 chunks; add SQL cosine later with pgvector)
        chunks = db.query(SkillChunk).filter(
            SkillChunk.embedding != None  # noqa: E711
        ).all()

        scored = []
        for chunk in chunks:
            try:
                emb = json.loads(chunk.embedding)
                sim = _cosine_similarity(query_emb, emb)
                if sim >= min_similarity:
                    scored.append((sim, chunk))
            except Exception:
                continue

        if not scored:
            return None

        scored.sort(key=lambda x: x[0], reverse=True)
        top_chunks = scored[:top_k]

        lines = ["## RELEVANT METHODOLOGY FROM SKILL LIBRARY"]
        seen_skills = set()
        for sim, chunk in top_chunks:
            skill = chunk.skill_name
            if skill not in seen_skills:
                lines.append(f"\n### From: {skill} (relevance: {sim:.2f})")
                seen_skills.add(skill)
            lines.append(chunk.content[:800])

        return "\n".join(lines)
    except Exception:
        return None
