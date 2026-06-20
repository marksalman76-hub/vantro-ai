"""Initial migration - Create core tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-06-20

This is the base schema for the multi-industrial SaaS platform.
It includes tables for organizations, workspaces, users, billing, credits, and audit logging.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema"""
    
    # Organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('website', sa.String(255)),
        sa.Column('industry', sa.String(100)),
        sa.Column('size', sa.String(50)),
        sa.Column('country', sa.String(2)),
        sa.Column('phone', sa.String(20)),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('stripe_customer_id', sa.String(255), unique=True),
        sa.Column('billing_email', sa.String(255)),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_name', 'organizations', ['name'])
    op.create_index('idx_slug', 'organizations', ['slug'])
    op.create_index('idx_org_status_created', 'organizations', ['status', 'created_at'])
    op.create_index('idx_org_industry', 'organizations', ['industry'])
    
    # Workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('workspace_type', sa.String(50), server_default='standard'),
        sa.Column('stripe_subscription_id', sa.String(255), unique=True),
        sa.Column('billing_cycle_start', sa.DateTime),
        sa.Column('billing_cycle_end', sa.DateTime),
        sa.Column('total_credits', sa.Integer, server_default='0'),
        sa.Column('used_credits', sa.Integer, server_default='0'),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'slug', name='uq_org_workspace_slug')
    )
    op.create_index('idx_workspace_slug', 'workspaces', ['slug'])
    op.create_index('idx_workspace_status_active', 'workspaces', ['status', 'is_active'])
    op.create_index('idx_workspace_org_active', 'workspaces', ['organization_id', 'is_active'])
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('phone', sa.String(20)),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('password_reset_token', sa.String(255), unique=True),
        sa.Column('password_reset_expires', sa.DateTime),
        sa.Column('email_verified', sa.Boolean, server_default='false'),
        sa.Column('email_verified_at', sa.DateTime),
        sa.Column('role', sa.String(50), server_default='member'),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_login', sa.DateTime),
        sa.Column('last_activity', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'email', name='uq_org_user_email')
    )
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_status_active', 'users', ['status', 'is_active'])
    op.create_index('idx_user_org_active', 'users', ['organization_id', 'is_active'])
    
    # Workspace Users table (many-to-many with roles)
    op.create_table(
        'workspace_users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role', sa.String(50), server_default='member'),
        sa.Column('permissions', postgresql.JSON, server_default='{}'),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_user')
    )
    op.create_index('idx_workspace_user_role', 'workspace_users', ['workspace_id', 'role'])
    
    # Subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=False, unique=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=False),
        sa.Column('stripe_price_id', sa.String(255), nullable=False),
        sa.Column('plan_name', sa.String(100), nullable=False),
        sa.Column('plan_price', sa.Float, nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('billing_interval', sa.String(50)),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('current_period_start', sa.DateTime),
        sa.Column('current_period_end', sa.DateTime),
        sa.Column('cancel_at', sa.DateTime),
        sa.Column('cancel_at_period_end', sa.Boolean, server_default='false'),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_subscription_status_active', 'subscriptions', ['status', 'workspace_id'])
    op.create_index('idx_subscription_customer', 'subscriptions', ['stripe_customer_id'])
    
    # Credit Ledger table
    op.create_table(
        'credit_ledger',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('operation_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('reference_id', sa.String(36)),
        sa.Column('reference_type', sa.String(50)),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ledger_workspace_date', 'credit_ledger', ['workspace_id', 'created_at'])
    op.create_index('idx_ledger_operation_type', 'credit_ledger', ['operation_type'])
    op.create_index('idx_ledger_reference', 'credit_ledger', ['reference_id', 'reference_type'])
    
    # Invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36), nullable=False),
        sa.Column('stripe_invoice_id', sa.String(255), nullable=False, unique=True),
        sa.Column('invoice_number', sa.String(50), nullable=False, unique=True),
        sa.Column('total_amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('paid', sa.Boolean, server_default='false'),
        sa.Column('invoice_date', sa.DateTime, nullable=False),
        sa.Column('due_date', sa.DateTime),
        sa.Column('paid_date', sa.DateTime),
        sa.Column('metadata', postgresql.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_invoice_workspace_date', 'invoices', ['workspace_id', 'invoice_date'])
    op.create_index('idx_invoice_status', 'invoices', ['status'])
    
    # Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36)),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('workspace_id', sa.String(36)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(36)),
        sa.Column('old_values', postgresql.JSON),
        sa.Column('new_values', postgresql.JSON),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('details', postgresql.JSON, server_default='{}'),
        sa.Column('success', sa.Boolean, server_default='true'),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_org_action', 'audit_logs', ['organization_id', 'action', 'created_at'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('idx_audit_user_action', 'audit_logs', ['user_id', 'action'])


def downgrade() -> None:
    """Drop all tables created in upgrade()"""
    
    op.drop_table('audit_logs')
    op.drop_table('invoices')
    op.drop_table('credit_ledger')
    op.drop_table('subscriptions')
    op.drop_table('workspace_users')
    op.drop_table('users')
    op.drop_table('workspaces')
    op.drop_table('organizations')