# app/routers/auth.py
"""Authentication routes — signup, login, Google OAuth, current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    UserCreate, UserLogin, GoogleAuth, Token, UserResponse,
    UserProfileUpdate, PasswordChange, MessageResponse, NotificationItem,
)
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_email,
    create_user,
    get_current_user,
)
from app.models import User, Employee, Policy, OnboardingWorkflow

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ─────────────────────────────────────────────────────────────
# POST /api/auth/signup
# ─────────────────────────────────────────────────────────────

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email and password."""
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_pw = hash_password(payload.password)
    user = create_user(db, email=payload.email, name=payload.name, hashed_password=hashed_pw)
    return user


# ─────────────────────────────────────────────────────────────
# POST /api/auth/login
# ─────────────────────────────────────────────────────────────

@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password, return JWT."""
    user = get_user_by_email(db, payload.email)
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=token)


# ─────────────────────────────────────────────────────────────
# POST /api/auth/google
# ─────────────────────────────────────────────────────────────

@router.post("/google", response_model=Token)
async def google_auth(payload: GoogleAuth, db: Session = Depends(get_db)):
    """
    Validate a Google OAuth ID token, create user if first login,
    and return a JWT.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        idinfo = id_token.verify_oauth2_token(
            payload.token,
            google_requests.Request(),
        )
        email = idinfo.get("email")
        name = idinfo.get("name", email)
        google_id = idinfo.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    # Find or create user
    user = get_user_by_email(db, email)
    if not user:
        user = create_user(db, email=email, name=name, google_id=google_id)
    elif not user.google_id:
        # Link Google account to existing user
        user.google_id = google_id
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=token)


# ─────────────────────────────────────────────────────────────
# GET /api/auth/me
# ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user


# ─────────────────────────────────────────────────────────────
# PUT /api/auth/profile
# ─────────────────────────────────────────────────────────────

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the current user's name and/or email."""
    if payload.email and payload.email != current_user.email:
        existing = get_user_by_email(db, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        current_user.email = payload.email
    if payload.name:
        current_user.name = payload.name
    db.commit()
    db.refresh(current_user)
    return current_user


# ─────────────────────────────────────────────────────────────
# PUT /api/auth/password
# ─────────────────────────────────────────────────────────────

@router.put("/password", response_model=MessageResponse)
async def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change the current user's password."""
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change not available for OAuth accounts",
        )
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return MessageResponse(message="Password changed successfully")


# ─────────────────────────────────────────────────────────────
# GET /api/auth/notifications
# ─────────────────────────────────────────────────────────────

@router.get("/notifications", response_model=list[NotificationItem])
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent activity as notifications (latest 20 items)."""
    notifications: list[NotificationItem] = []

    # Recent onboarding workflows
    workflows = (
        db.query(OnboardingWorkflow)
        .order_by(OnboardingWorkflow.created_at.desc())
        .limit(10)
        .all()
    )
    for wf in workflows:
        emp = wf.employee
        status_label = wf.status.value
        if status_label == "completed":
            title = f"Onboarding completed"
            desc = f"{emp.name}'s onboarding finished successfully"
        elif status_label == "failed":
            title = f"Onboarding failed"
            desc = f"{emp.name}'s onboarding encountered an error"
        elif status_label == "running":
            title = f"Onboarding in progress"
            desc = f"{emp.name}'s onboarding is currently running"
        else:
            title = f"Onboarding queued"
            desc = f"{emp.name}'s onboarding is pending"
        notifications.append(NotificationItem(
            id=f"wf-{wf.id}",
            title=title,
            description=desc,
            type="onboarding",
            timestamp=wf.created_at,
        ))

    # Recently added employees (last 5)
    recent_employees = (
        db.query(Employee)
        .order_by(Employee.created_at.desc())
        .limit(5)
        .all()
    )
    for emp in recent_employees:
        notifications.append(NotificationItem(
            id=f"emp-{emp.id}",
            title="New employee added",
            description=f"{emp.name} ({emp.department}) starts {emp.start_date}",
            type="employee",
            timestamp=emp.created_at,
        ))

    # Recently uploaded policies (last 5)
    recent_policies = (
        db.query(Policy)
        .order_by(Policy.uploaded_at.desc())
        .limit(5)
        .all()
    )
    for pol in recent_policies:
        notifications.append(NotificationItem(
            id=f"pol-{pol.id}",
            title="Policy uploaded",
            description=f"\"{pol.title}\" was uploaded and {'embedded' if pol.is_embedded else 'is processing'}",
            type="policy",
            timestamp=pol.uploaded_at,
        ))

    # Sort all by timestamp descending, return top 20
    notifications.sort(key=lambda n: n.timestamp, reverse=True)
    return notifications[:20]
