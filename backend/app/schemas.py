# app/schemas.py
"""Pydantic V2 schemas for request / response validation."""

from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Auth Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleAuth(BaseModel):
    token: str  # Google OAuth ID token


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class NotificationItem(BaseModel):
    id: str
    title: str
    description: str
    type: str  # "onboarding" | "employee" | "policy" | "approval"
    timestamp: datetime
    read: bool = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Employee Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    role: str
    department: str
    start_date: date
    manager_email: Optional[EmailStr] = None
    buddy_email: Optional[EmailStr] = None
    jurisdiction: str = Field(default="US", description="Country code (e.g., US, UK, AE, DE, SG)")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[date] = None
    manager_email: Optional[EmailStr] = None
    buddy_email: Optional[EmailStr] = None
    jurisdiction: Optional[str] = None
    status: Optional[Literal["pending", "onboarding", "completed", "failed"]] = None


class EmployeeResponse(EmployeeBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Policy Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class PolicyResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_size: Optional[int] = None
    is_embedded: bool
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Jurisdiction Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class JurisdictionInfo(BaseModel):
    """Summary info for a single jurisdiction."""
    code: str
    name: str
    document_types: list[str] = []


class JurisdictionTemplateResponse(BaseModel):
    id: int
    jurisdiction_code: str
    jurisdiction_name: str
    document_type: str
    template_content: str
    legal_requirements: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Document Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class GeneratedDocumentResponse(BaseModel):
    id: int
    employee_id: int
    document_type: str
    jurisdiction: str
    content: str
    status: str
    version: int
    generated_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None

    model_config = {"from_attributes": True}


class DocumentUpdateRequest(BaseModel):
    content: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Approval Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ApprovalRequestResponse(BaseModel):
    id: int
    employee_id: int
    document_id: int
    status: str
    reviewer_id: Optional[int] = None
    comments: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    # Nested info for display
    employee_name: Optional[str] = None
    document_type: Optional[str] = None
    document_content: Optional[str] = None
    jurisdiction: Optional[str] = None

    model_config = {"from_attributes": True}


class ApprovalActionRequest(BaseModel):
    comments: Optional[str] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Chat Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    sources: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatConversationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: str
    started_at: datetime
    last_message_at: datetime
    messages: list[ChatMessageResponse] = []

    model_config = {"from_attributes": True}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Compliance Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ComplianceItemCreate(BaseModel):
    employee_id: int
    item_type: str = Field(..., description="visa, work_permit, certification, training, equipment")
    description: str
    expiry_date: date


class ComplianceItemResponse(BaseModel):
    id: int
    employee_id: int
    item_type: str
    description: str
    expiry_date: date
    status: str
    reminder_sent: bool
    created_at: datetime
    # Enriched fields
    employee_name: Optional[str] = None
    days_remaining: Optional[int] = None

    model_config = {"from_attributes": True}


class ComplianceSummary(BaseModel):
    valid: int
    expiring_soon: int
    expired: int
    total: int


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Onboarding Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class OnboardingStepResponse(BaseModel):
    id: int
    step_type: str
    step_order: int
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None
    requires_approval: bool = False
    approval_status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OnboardingWorkflowResponse(BaseModel):
    id: int
    employee_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    steps: list[OnboardingStepResponse] = []

    model_config = {"from_attributes": True}


class OnboardingStartResponse(BaseModel):
    workflow_id: int
    employee_id: int
    message: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Calendar Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class CalendarEventCreate(BaseModel):
    employee_id: int
    event_type: str = Field(..., description="orientation | manager_1on1 | buddy_meetup")
    title: str
    description: Optional[str] = None
    date: date
    duration_minutes: int = 60
    attendees: list[str] = []


class CalendarEventResponse(BaseModel):
    id: str
    title: str
    date: date
    status: str  # "created" | "mock"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Generic Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class MessageResponse(BaseModel):
    message: str


class BulkUploadResponse(BaseModel):
    total: int
    created: int
    errors: list[str] = []
