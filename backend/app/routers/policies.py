# app/routers/policies.py
"""Policy document routes — upload PDF, list, delete."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PolicyResponse, MessageResponse
from app.services import policy as policy_service
from app.services.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/api/policies", tags=["Policies"])


# ─────────────────────────────────────────────────────────────
# GET /api/policies/
# ─────────────────────────────────────────────────────────────

@router.get("/", response_model=list[PolicyResponse])
async def list_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all uploaded policy documents."""
    return policy_service.get_all_policies(db)


# ─────────────────────────────────────────────────────────────
# POST /api/policies/upload
# ─────────────────────────────────────────────────────────────

@router.post("/upload", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def upload_policy(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF policy document."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    policy = policy_service.save_policy(db, title=title, filename=file.filename, file_content=content)
    return policy


# ─────────────────────────────────────────────────────────────
# GET /api/policies/{id}
# ─────────────────────────────────────────────────────────────

@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single policy by ID."""
    policy = policy_service.get_policy_by_id(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


# ─────────────────────────────────────────────────────────────
# DELETE /api/policies/{id}
# ─────────────────────────────────────────────────────────────

@router.delete("/{policy_id}", response_model=MessageResponse)
async def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a policy document and its file."""
    deleted = policy_service.delete_policy(db, policy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Policy not found")
    return MessageResponse(message="Policy deleted successfully")
