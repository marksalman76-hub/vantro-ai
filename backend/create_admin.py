#!/usr/bin/env python3
"""Create or update admin user for mark.salman76@gmail.com"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

load_dotenv()

from app.auth import hash_password
from app.models import User

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/multi_industrial_dev")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "mark.salman76@gmail.com")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def create_admin_user(password: str = "Admin123"):
    """Create or update admin user"""
    session = Session()

    try:
        # Check if user exists (use lowercase email)
        user = session.query(User).filter(User.email == ADMIN_EMAIL.lower()).first()

        if user:
            # Update existing user
            user.password_hash = hash_password(password)
            user.is_admin = True
            session.commit()
            print(f"[OK] Updated admin user: {ADMIN_EMAIL}")
            print(f"   Password set to: {password}")
        else:
            # Create new user
            user_id = str(uuid.uuid4())
            user = User(
                id=user_id,
                email=ADMIN_EMAIL.lower(),
                password_hash=hash_password(password),
                name="Admin",
                is_admin=True,
                is_active=True,
                created_at=datetime.utcnow(),
            )
            session.add(user)
            session.commit()
            print(f"[OK] Created admin user: {ADMIN_EMAIL}")
            print(f"   Password: {password}")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    pw = sys.argv[1] if len(sys.argv) > 1 else "Admin123"
    create_admin_user(pw)
