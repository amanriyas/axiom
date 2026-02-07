# app/services/approval.py
"""Approval workflow service — manages human review of AI-generated documents."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models import (
    ApprovalRequest,
    ApprovalStatus,
    GeneratedDocument,
    DocumentStatus,
    OnboardingWorkflow,
    WorkflowStatus,
)


def create_approval_request(db: Session, employee_id: int, document_id: int) -> ApprovalRequest:
    """Create a new approval request for a generated document."""
    approval = ApprovalRequest(
        employee_id=employee_id,
        document_id=document_id,
        status=ApprovalStatus.PENDING,
    )
    db.add(approval)

    # Update document status
    doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == document_id).first()
    if doc:
        doc.status = DocumentStatus.PENDING_APPROVAL

    db.commit()
    db.refresh(approval)
    return approval


def approve_document(db: Session, approval_id: int, reviewer_id: int, comments: Optional[str] = None) -> ApprovalRequest:
    """Approve a document — marks both approval and document as approved."""
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        raise ValueError("Approval request not found")

    approval.status = ApprovalStatus.APPROVED
    approval.reviewer_id = reviewer_id
    approval.comments = comments
    approval.reviewed_at = datetime.utcnow()

    # Update document status
    doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == approval.document_id).first()
    if doc:
        doc.status = DocumentStatus.APPROVED
        doc.approved_at = datetime.utcnow()
        doc.approved_by = reviewer_id

    # Check if all approvals for this employee are approved → resume workflow
    _check_all_approvals_complete(db, approval.employee_id)

    db.commit()
    db.refresh(approval)
    return approval


def reject_document(db: Session, approval_id: int, reviewer_id: int, comments: Optional[str] = None) -> ApprovalRequest:
    """Reject a document."""
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        raise ValueError("Approval request not found")

    approval.status = ApprovalStatus.REJECTED
    approval.reviewer_id = reviewer_id
    approval.comments = comments
    approval.reviewed_at = datetime.utcnow()

    # Update document status back to draft
    doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == approval.document_id).first()
    if doc:
        doc.status = DocumentStatus.DRAFT

    db.commit()
    db.refresh(approval)
    return approval


def request_revision(db: Session, approval_id: int, reviewer_id: int, comments: Optional[str] = None) -> ApprovalRequest:
    """Request revision of a document."""
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        raise ValueError("Approval request not found")

    approval.status = ApprovalStatus.REVISION_REQUESTED
    approval.reviewer_id = reviewer_id
    approval.comments = comments
    approval.reviewed_at = datetime.utcnow()

    # Update document status back to draft
    doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == approval.document_id).first()
    if doc:
        doc.status = DocumentStatus.DRAFT

    db.commit()
    db.refresh(approval)
    return approval


def get_pending_approvals(db: Session) -> list[ApprovalRequest]:
    """Get all pending approval requests."""
    return (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.status == ApprovalStatus.PENDING)
        .order_by(ApprovalRequest.created_at.desc())
        .all()
    )


def get_all_approvals(db: Session, status_filter: Optional[str] = None) -> list[ApprovalRequest]:
    """Get all approval requests, optionally filtered by status."""
    query = db.query(ApprovalRequest)
    if status_filter:
        query = query.filter(ApprovalRequest.status == status_filter)
    return query.order_by(ApprovalRequest.created_at.desc()).all()


def get_approval_by_id(db: Session, approval_id: int) -> Optional[ApprovalRequest]:
    """Get a single approval request by ID."""
    return db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()


def get_approvals_by_employee(db: Session, employee_id: int) -> list[ApprovalRequest]:
    """Get all approval requests for an employee."""
    return (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.employee_id == employee_id)
        .order_by(ApprovalRequest.created_at.desc())
        .all()
    )


def _check_all_approvals_complete(db: Session, employee_id: int):
    """Check if all pending approvals for an employee are complete. If so, resume the workflow."""
    pending = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.employee_id == employee_id,
            ApprovalRequest.status == ApprovalStatus.PENDING,
        )
        .count()
    )

    if pending == 0:
        # All documents approved — resume the workflow if it was awaiting approval
        workflow = (
            db.query(OnboardingWorkflow)
            .filter(
                OnboardingWorkflow.employee_id == employee_id,
                OnboardingWorkflow.status == WorkflowStatus.AWAITING_APPROVAL,
            )
            .first()
        )
        if workflow:
            workflow.status = WorkflowStatus.RUNNING
            db.commit()
            # Kick off background execution of remaining steps
            import asyncio
            from app.database import SessionLocal

            async def _continue_workflow(wf_id: int):
                from app.services.orchestrator import run_workflow
                bg_db = SessionLocal()
                try:
                    await run_workflow(bg_db, wf_id)
                except Exception as e:
                    print(f"⚠️  Background workflow {wf_id} resume error: {e}")
                finally:
                    bg_db.close()

            try:
                loop = asyncio.get_event_loop()
                loop.create_task(_continue_workflow(workflow.id))
            except RuntimeError:
                pass  # No event loop — SSE stream will handle it
