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
    DETECT_JURISDICTION = "detect_jurisdiction"
    EMPLOYMENT_CONTRACT = "employment_contract"
    NDA = "nda"
    EQUITY_AGREEMENT = "equity_agreement"
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
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class ComplianceStatus(str, enum.Enum):
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"


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
    jurisdiction = Column(String(10), default="US", nullable=False)
    status = Column(SAEnum(EmployeeStatus), default=EmployeeStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workflows = relationship("OnboardingWorkflow", back_populates="employee", cascade="all, delete-orphan")
    documents = relationship("GeneratedDocument", back_populates="employee", cascade="all, delete-orphan")
    compliance_items = relationship("ComplianceItem", back_populates="employee", cascade="all, delete-orphan")


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
    requires_approval = Column(Boolean, default=False, nullable=False)
    approval_status = Column(String(50), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    workflow = relationship("OnboardingWorkflow", back_populates="steps")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Jurisdiction Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class JurisdictionTemplate(Base):
    """Jurisdiction-specific document templates with legal requirements."""

    __tablename__ = "jurisdiction_templates"

    id = Column(Integer, primary_key=True, index=True)
    jurisdiction_code = Column(String(10), nullable=False, index=True)
    jurisdiction_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)
    template_content = Column(Text, nullable=False)
    legal_requirements = Column(Text, nullable=True)  # JSON string of required clauses
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Document Generation Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class GeneratedDocument(Base):
    """AI-generated documents (contracts, NDAs, etc.) for employees."""

    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    document_type = Column(String(100), nullable=False)
    jurisdiction = Column(String(10), nullable=False, default="US")
    content = Column(Text, nullable=False)
    status = Column(SAEnum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    employee = relationship("Employee", back_populates="documents")
    approver = relationship("User", foreign_keys=[approved_by])
    approval_requests = relationship("ApprovalRequest", back_populates="document", cascade="all, delete-orphan")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Approval Workflow Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ApprovalRequest(Base):
    """Human approval requests for AI-generated documents."""

    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("generated_documents.id"), nullable=False)
    status = Column(SAEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    employee = relationship("Employee")
    document = relationship("GeneratedDocument", back_populates="approval_requests")
    reviewer = relationship("User", foreign_keys=[reviewer_id])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Chat / Policy Chatbot Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ChatConversation(Base):
    """A chat session with the policy assistant."""

    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), default="New Conversation", nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan",
                            order_by="ChatMessage.created_at")
    user = relationship("User")


class ChatMessage(Base):
    """A single message in a chat conversation."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON array of policy chunks used
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Compliance Models
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ComplianceItem(Base):
    """Compliance tracking items (visas, certifications, training, etc.)."""

    __tablename__ = "compliance_items"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    item_type = Column(String(50), nullable=False)  # visa, work_permit, certification, training, equipment
    description = Column(String(500), nullable=False)
    expiry_date = Column(Date, nullable=False)
    status = Column(SAEnum(ComplianceStatus), default=ComplianceStatus.VALID, nullable=False)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="compliance_items")
