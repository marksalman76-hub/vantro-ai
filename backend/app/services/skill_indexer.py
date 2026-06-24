"""
Skill indexer: reads SKILL.md files from ~/.claude/skills/,
chunks by section, embeds with OpenAI, stores in skill_chunks table.
"""
import json
import os
import re
import pathlib
from sqlalchemy.orm import Session

SKILLS_DIR = pathlib.Path.home() / ".claude" / "skills"
MAX_CHUNK_CHARS = 1200
MIN_CHUNK_CHARS = 100

# Claude Code tool references to strip (these confuse backend agents)
TOOL_REF_PATTERNS = [
    r'(?i)(use the (Read|Write|Bash|Glob|Grep|Agent|Edit) tool[^.]*\.)',
    r'(?i)(call (Read|Write|Bash|Glob|Grep|Agent|Edit)\([^)]*\))',
    r'(?i)(invoke the (Read|Write|Bash|Glob|Grep|Agent|Edit) tool[^.]*\.)',
    r'(?i)\bTodoWrite\b[^.]*\.',
    r'(?i)\bTaskCreate\b[^.]*\.',
]


def load_skill_files() -> list[dict]:
    """Find all SKILL.md files under SKILLS_DIR."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        content = skill_file.read_text(encoding="utf-8", errors="replace")
        if len(content.strip()) < 100:
            continue
        skills.append({
            "name": skill_dir.name,
            "content": content,
            "path": str(skill_file),
        })
    return skills


def clean_skill_content(content: str) -> str:
    """Strip Claude Code tool references, keep methodology."""
    for pattern in TOOL_REF_PATTERNS:
        content = re.sub(pattern, "", content)
    # Strip YAML frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    return content.strip()


def chunk_skill(content: str, skill_name: str) -> list[str]:
    """Split skill content into chunks by ## headers."""
    content = clean_skill_content(content)
    # Split on ## (section) headings
    sections = re.split(r'\n(?=##\s)', content)
    chunks = []
    current = ""
    for section in sections:
        if len(current) + len(section) < MAX_CHUNK_CHARS:
            current += "\n" + section
        else:
            if len(current.strip()) >= MIN_CHUNK_CHARS:
                chunks.append(current.strip())
            current = section
    if len(current.strip()) >= MIN_CHUNK_CHARS:
        chunks.append(current.strip())
    # Prefix each chunk with skill name for context
    return [f"[SKILL: {skill_name}]\n{chunk}" for chunk in chunks]


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Embed chunks using OpenAI text-embedding-3-small."""
    import openai
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    embeddings = []
    # Batch in groups of 20
    for i in range(0, len(chunks), 20):
        batch = chunks[i:i + 20]
        resp = client.embeddings.create(model="text-embedding-3-small", input=batch)
        embeddings.extend([item.embedding for item in resp.data])
    return embeddings


def get_skills_needing_index(db: Session) -> list[str]:
    """
    Compare ~/.claude/skills/ against skill_chunks table.
    Returns skill names that are new (never indexed) OR have a SKILL.md
    modified more recently than the last indexed timestamp.
    Silent on any error — returns [] so nothing blocks job execution.
    """
    from datetime import datetime
    try:
        from app.models.skill_chunk import SkillChunk
        from sqlalchemy import func

        if not SKILLS_DIR.exists():
            return []

        # last indexed timestamp per skill (UTC-naive for comparison)
        indexed: dict[str, datetime] = {}
        for row in db.query(
            SkillChunk.skill_name,
            func.max(SkillChunk.updated_at).label("latest"),
        ).group_by(SkillChunk.skill_name).all():
            ts = row.latest
            if ts is not None:
                # strip tz if present so comparison is uniform
                indexed[row.skill_name] = ts.replace(tzinfo=None) if hasattr(ts, "tzinfo") else ts

        needing: list[str] = []
        for skill_dir in SKILLS_DIR.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists() or skill_file.stat().st_size < 100:
                continue
            name = skill_dir.name
            if name not in indexed:
                needing.append(name)  # brand new skill
            else:
                mtime = datetime.utcfromtimestamp(skill_file.stat().st_mtime)
                if mtime > indexed[name]:
                    needing.append(name)  # SKILL.md updated since last index
        return needing
    except Exception:
        return []


def index_skills_by_name(db: Session, skill_names: list[str]) -> dict:
    """Index a specific subset of skills by name. Used by auto-reindex."""
    from app.models.skill_chunk import SkillChunk

    if not SKILLS_DIR.exists() or not skill_names:
        return {"indexed": 0, "skills": [], "total_chunks": 0, "failed": []}

    target = set(skill_names)
    skills = [s for s in load_skill_files() if s["name"] in target]
    total_chunks = 0
    indexed_skills: list[str] = []
    failed_skills: list[dict] = []

    for skill in skills:
        try:
            chunks = chunk_skill(skill["content"], skill["name"])
            if not chunks:
                continue
            embeddings = embed_chunks(chunks)
            db.query(SkillChunk).filter(SkillChunk.skill_name == skill["name"]).delete()
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                db.add(SkillChunk(
                    skill_name=skill["name"],
                    chunk_index=i,
                    content=chunk,
                    embedding=json.dumps(emb),
                    char_count=len(chunk),
                ))
            db.commit()
            total_chunks += len(chunks)
            indexed_skills.append(skill["name"])
        except Exception as e:
            failed_skills.append({"skill": skill["name"], "error": str(e)})
            db.rollback()

    return {
        "indexed": len(indexed_skills),
        "skills": indexed_skills,
        "total_chunks": total_chunks,
        "failed": failed_skills,
    }


def index_all_skills(db: Session) -> dict:
    """
    Main entry point. Indexes all skill files into skill_chunks table.
    Re-indexes on each call (delete existing for skill, re-insert).
    Returns stats dict.
    """
    from app.models.skill_chunk import SkillChunk

    skills = load_skill_files()
    total_chunks = 0
    indexed_skills = []
    failed_skills = []

    for skill in skills:
        try:
            chunks = chunk_skill(skill["content"], skill["name"])
            if not chunks:
                continue
            embeddings = embed_chunks(chunks)
            # Delete existing chunks for this skill
            db.query(SkillChunk).filter(SkillChunk.skill_name == skill["name"]).delete()
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                db.add(SkillChunk(
                    skill_name=skill["name"],
                    chunk_index=i,
                    content=chunk,
                    embedding=json.dumps(emb),
                    char_count=len(chunk),
                ))
            db.commit()
            total_chunks += len(chunks)
            indexed_skills.append(skill["name"])
        except Exception as e:
            failed_skills.append({"skill": skill["name"], "error": str(e)})
            db.rollback()

    return {
        "indexed": len(indexed_skills),
        "skills": indexed_skills,
        "total_chunks": total_chunks,
        "failed": failed_skills,
    }
