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
# Onboarding Schemas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class OnboardingStepResponse(BaseModel):
    id: int
    step_type: str
    step_order: int
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None
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
