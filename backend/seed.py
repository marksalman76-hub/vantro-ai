"""
Seed script to create admin account and initial data
Run: python backend/seed.py
"""

import os
import uuid
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

load_dotenv()

from app.models import (
    Base, Organization, Workspace, User, WorkspaceUser, Subscription
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/multi_industrial_dev")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def seed_admin():
    """Create owner organization, workspace, and admin user"""
    session = Session()
    
    try:
        # Check if admin already exists
        existing_org = session.query(Organization).filter_by(slug="owner").first()
        if existing_org:
            print("✅ Admin account already exists (owner org found)")
            return
        
        # Create Owner Organization
        org_id = str(uuid.uuid4())
        org = Organization(
            id=org_id,
            name="Owner Account",
            slug="owner",
            email="admin@trance-formation.com.au",
            status="active",
            is_active=True
        )
        session.add(org)
        session.flush()
        print(f"✅ Created organization: {org.name}")
        
        # Create Owner Workspace
        workspace_id = str(uuid.uuid4())
        workspace = Workspace(
            id=workspace_id,
            organization_id=org_id,
            name="Default Workspace",
            slug="default",
            workspace_type="standard",
            status="active",
            is_active=True
        )
        session.add(workspace)
        session.flush()
        print(f"✅ Created workspace: {workspace.name}")
        
        # Create Admin User
        user_id = str(uuid.uuid4())
        admin_user = User(
            id=user_id,
            organization_id=org_id,
            email="admin@trance-formation.com.au",
            first_name="Admin",
            last_name="User",
            password_hash="hashed_password_placeholder",  # TODO: Hash real password
            email_verified=True,
            email_verified_at=datetime.utcnow(),
            role="admin",
            status="active",
            is_active=True
        )
        session.add(admin_user)
        session.flush()
        print(f"✅ Created admin user: {admin_user.email}")
        
        # Assign user to workspace with admin role
        workspace_user_id = str(uuid.uuid4())
        workspace_user = WorkspaceUser(
            id=workspace_user_id,
            workspace_id=workspace_id,
            user_id=user_id,
            role="admin",
            permissions={"all": True},
            status="active"
        )
        session.add(workspace_user)
        session.flush()
        print(f"✅ Assigned admin user to workspace with admin role")
        
        # Create trial subscription
        subscription_id = str(uuid.uuid4())
        subscription = Subscription(
            id=subscription_id,
            workspace_id=workspace_id,
            stripe_subscription_id="trial_000_owner",
            stripe_customer_id="cus_owner_trial",
            stripe_price_id="price_trial",
            plan_name="Trial",
            plan_price=0.0,
            currency="AUD",
            billing_interval="monthly",
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=14)
        )
        session.add(subscription)
        session.flush()
        print(f"✅ Created trial subscription (14 days)")
        
        session.commit()
        print("\n✅ Seeding complete!")
        print("\nAdmin account created:")
        print(f"  Organization: {org.slug}")
        print(f"  Workspace: {workspace.slug}")
        print(f"  Email: admin@trance-formation.com.au")
        print(f"  Role: admin")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_admin()