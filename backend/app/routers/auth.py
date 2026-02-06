# app/routers/auth.py
"""Authentication routes — signup, login, Google OAuth, current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserLogin, GoogleAuth, Token, UserResponse, MessageResponse
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_email,
    create_user,
    get_current_user,
)
from app.models import User

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

    token = create_access_token(data={"sub": user.id, "email": user.email})
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

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return Token(access_token=token)


# ─────────────────────────────────────────────────────────────
# GET /api/auth/me
# ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user
