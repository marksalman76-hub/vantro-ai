"""
Core Database Models for Multi-Industrial SaaS Platform

This schema is designed to be industry-agnostic yet extensible.
All timestamp fields use UTC timezone.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Enum, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class Organization(Base):
    """Organization/Company using the platform"""
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    website = Column(String(255))
    industry = Column(String(100))
    size = Column(String(50))
    country = Column(String(2))
    phone = Column(String(20))
    custom_metadata = Column(JSON, default={})
    
    stripe_customer_id = Column(String(255), unique=True, index=True)
    billing_email = Column(String(255))
    
    status = Column(String(50), default="active")
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspaces = relationship("Workspace", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_org_status_created', 'status', 'created_at'),
        Index('idx_org_industry', 'industry'),
    )


class Workspace(Base):
    """Workspace/Project within an organization (for multi-tenant billing)"""
    __tablename__ = "workspaces"
    
    id = Column(String(36), primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    workspace_type = Column(String(50), default="standard")
    
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    billing_cycle_start = Column(DateTime)
    billing_cycle_end = Column(DateTime)
    
    total_credits = Column(Integer, default=0)
    used_credits = Column(Integer, default=0)
    
    status = Column(String(50), default="active")
    is_active = Column(Boolean, default=True, index=True)
    
    custom_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="workspaces")
    users = relationship("WorkspaceUser", back_populates="workspace", cascade="all, delete-orphan")
    credits = relationship("CreditLedger", back_populates="workspace", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="workspace", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'slug', name='uq_org_workspace_slug'),
        Index('idx_workspace_status_active', 'status', 'is_active'),
        Index('idx_workspace_org_active', 'organization_id', 'is_active'),
    )


class User(Base):
    """Team member/user in the organization"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    
    password_hash = Column(String(255))
    password_reset_token = Column(String(255), unique=True, index=True)
    password_reset_expires = Column(DateTime)
    
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    
    role = Column(String(50), default="member")
    
    status = Column(String(50), default="active")
    is_active = Column(Boolean, default=True, index=True)
    
    last_login = Column(DateTime)
    last_activity = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="users")
    workspace_roles = relationship("WorkspaceUser", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'email', name='uq_org_user_email'),
        Index('idx_user_status_active', 'status', 'is_active'),
        Index('idx_user_org_active', 'organization_id', 'is_active'),
    )


class WorkspaceUser(Base):
    """User roles within specific workspaces"""
    __tablename__ = "workspace_users"
    
    id = Column(String(36), primary_key=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    role = Column(String(50), default="member")
    
    permissions = Column(JSON, default={})
    
    status = Column(String(50), default="active")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="users")
    user = relationship("User", back_populates="workspace_roles")
    
    __table_args__ = (
        UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_user'),
        Index('idx_workspace_user_role', 'workspace_id', 'role'),
    )


class Subscription(Base):
    """Stripe subscriptions and billing plans"""
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    stripe_subscription_id = Column(String(255), unique=True, nullable=False, index=True)
    stripe_customer_id = Column(String(255), nullable=False, index=True)
    stripe_price_id = Column(String(255), nullable=False)
    
    plan_name = Column(String(100), nullable=False)
    plan_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    billing_interval = Column(String(50))
    
    status = Column(String(50), default="active")
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    
    custom_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="subscriptions")
    
    __table_args__ = (
        Index('idx_subscription_status_active', 'status', 'workspace_id'),
        Index('idx_subscription_customer', 'stripe_customer_id'),
    )


class CreditLedger(Base):
    """Credit usage tracking and billing"""
    __tablename__ = "credit_ledger"
    
    id = Column(String(36), primary_key=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    amount = Column(Integer, nullable=False)
    operation_type = Column(String(50), nullable=False)
    description = Column(Text)
    
    reference_id = Column(String(36), index=True)
    reference_type = Column(String(50))
    
    custom_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    workspace = relationship("Workspace", back_populates="credits")
    
    __table_args__ = (
        Index('idx_ledger_workspace_date', 'workspace_id', 'created_at'),
        Index('idx_ledger_operation_type', 'operation_type'),
        Index('idx_ledger_reference', 'reference_id', 'reference_type'),
    )


class Invoice(Base):
    """Invoice records for billing"""
    __tablename__ = "invoices"
    
    id = Column(String(36), primary_key=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    stripe_invoice_id = Column(String(255), unique=True, nullable=False, index=True)
    
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    status = Column(String(50), default="draft")
    paid = Column(Boolean, default=False)
    
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    
    custom_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_invoice_workspace_date', 'workspace_id', 'invoice_date'),
        Index('idx_invoice_status', 'status'),
    )


class AuditLog(Base):
    """Audit trail for compliance and debugging"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True)
    
    user_id = Column(String(36), index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), index=True)
    
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(36), index=True)
    
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    ip_address = Column(String(45))
    user_agent = Column(Text)
    details = Column(JSON, default={})
    
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_audit_org_action', 'organization_id', 'action', 'created_at'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_user_action', 'user_id', 'action'),
    )
