#!/usr/bin/env python3
"""CLI: index all ~/.claude/skills/ SKILL.md files into pgvector.

Usage: python scripts/index_skills.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.services.skill_indexer import index_all_skills


def main():
    print("Indexing skills into pgvector...")
    db = SessionLocal()
    try:
        result = index_all_skills(db)
        print(f"Indexed {result['indexed']} skills, {result['total_chunks']} chunks")
        for s in result["skills"]:
            print(f"  - {s}")
        if result["failed"]:
            print("Failed:")
            for f in result["failed"]:
                print(f"  - {f['skill']}: {f['error']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
