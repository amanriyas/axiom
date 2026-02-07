# app/models.py
"""SQLAlchemy ORM models for the Zero-Touch Onboarding platform."""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enums
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HR = "hr"
    VIEWER = "viewer"


class EmployeeStatus(str, enum.Enum):
    PENDING = "pending"
    ONBOARDING = "onboarding"
    COMPLETED = "completed"
    FAILED = "failed"


class StepType(str, enum.Enum):
    PARSE_DATA = "parse_data"
    WELCOME_EMAIL = "welcome_email"
    OFFER_LETTER = "offer_letter"
    PLAN_30_60_90 = "plan_30_60_90"
    SCHEDULE_EVENTS = "schedule_events"
    EQUIPMENT_REQUEST = "equipment_request"


class StepStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class User(Base):
    """Registered users (HR admins, viewers) who access the platform."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # nullable for Google OAuth users
    name = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.HR, nullable=False)
    google_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Employee(Base):
    """Employees being onboarded — imported via CSV or created manually."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    manager_email = Column(String(255), nullable=True)
    buddy_email = Column(String(255), nullable=True)
    status = Column(SAEnum(EmployeeStatus), default=EmployeeStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workflows = relationship("OnboardingWorkflow", back_populates="employee", cascade="all, delete-orphan")


class Policy(Base):
    """Uploaded policy documents used for RAG-based document generation."""

    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    content_hash = Column(String(64), nullable=True)
    file_size = Column(Integer, nullable=True)
    is_embedded = Column(Boolean, default=False, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class OnboardingWorkflow(Base):
    """A single onboarding workflow instance for an employee."""

    __tablename__ = "onboarding_workflows"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    status = Column(SAEnum(WorkflowStatus), default=WorkflowStatus.PENDING, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="workflows")
    steps = relationship("OnboardingStep", back_populates="workflow", cascade="all, delete-orphan",
                         order_by="OnboardingStep.step_order")


class OnboardingStep(Base):
    """Individual step within an onboarding workflow."""

    __tablename__ = "onboarding_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("onboarding_workflows.id"), nullable=False)
    step_type = Column(SAEnum(StepType), nullable=False)
    step_order = Column(Integer, nullable=False)
    status = Column(SAEnum(StepStatus), default=StepStatus.PENDING, nullable=False)
    result = Column(Text, nullable=True)  # JSON string of step output
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    workflow = relationship("OnboardingWorkflow", back_populates="steps")
