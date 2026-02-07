# app/routers/approvals.py
"""Approval workflow routes — review and approve AI-generated documents."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ApprovalRequest, GeneratedDocument, Employee
from app.schemas import ApprovalRequestResponse, ApprovalActionRequest
from app.services.auth import get_current_user
from app.services.approval import (
    get_all_approvals,
    get_pending_approvals,
    get_approval_by_id,
    get_approvals_by_employee,
    approve_document,
    reject_document,
    request_revision,
)

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])


def _enrich_approval(approval: ApprovalRequest, db: Session) -> dict:
    """Add nested employee and document info to an approval response."""
    employee = db.query(Employee).filter(Employee.id == approval.employee_id).first()
    document = db.query(GeneratedDocument).filter(GeneratedDocument.id == approval.document_id).first()

    return {
        "id": approval.id,
        "employee_id": approval.employee_id,
        "document_id": approval.document_id,
        "status": approval.status.value if hasattr(approval.status, "value") else approval.status,
        "reviewer_id": approval.reviewer_id,
        "comments": approval.comments,
        "created_at": approval.created_at,
        "reviewed_at": approval.reviewed_at,
        "employee_name": employee.name if employee else None,
        "document_type": document.document_type if document else None,
        "document_content": document.content if document else None,
        "jurisdiction": document.jurisdiction if document else None,
    }


@router.get("/", response_model=list[ApprovalRequestResponse])
async def list_approvals(
    status: str | None = Query(None, description="Filter by status: pending, approved, rejected, revision_requested"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all approval requests, optionally filtered by status."""
    approvals = get_all_approvals(db, status_filter=status)
    return [_enrich_approval(a, db) for a in approvals]


@router.get("/pending/count")
async def get_pending_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the count of pending approvals (for sidebar badge)."""
    pending = get_pending_approvals(db)
    return {"count": len(pending)}


@router.get("/{approval_id}", response_model=ApprovalRequestResponse)
async def get_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single approval request with full details."""
    approval = get_approval_by_id(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return _enrich_approval(approval, db)


@router.post("/{approval_id}/approve", response_model=ApprovalRequestResponse)
async def approve(
    approval_id: int,
    payload: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a document."""
    try:
        approval = approve_document(db, approval_id, current_user.id, payload.comments)
        return _enrich_approval(approval, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{approval_id}/reject", response_model=ApprovalRequestResponse)
async def reject(
    approval_id: int,
    payload: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a document."""
    try:
        approval = reject_document(db, approval_id, current_user.id, payload.comments)
        return _enrich_approval(approval, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{approval_id}/revision", response_model=ApprovalRequestResponse)
async def revision(
    approval_id: int,
    payload: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Request revision of a document."""
    try:
        approval = request_revision(db, approval_id, current_user.id, payload.comments)
        return _enrich_approval(approval, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/employee/{employee_id}", response_model=list[ApprovalRequestResponse])
async def list_employee_approvals(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all approvals for a specific employee."""
    approvals = get_approvals_by_employee(db, employee_id)
    return [_enrich_approval(a, db) for a in approvals]
