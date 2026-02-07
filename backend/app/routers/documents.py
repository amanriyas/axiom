# app/routers/documents.py
"""Document management routes — view, edit, download generated documents."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import GeneratedDocumentResponse, DocumentUpdateRequest
from app.services.auth import get_current_user
from app.services.document_generator import (
    get_documents_by_employee,
    get_document_by_id,
    update_document_content,
)

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("/employee/{employee_id}", response_model=list[GeneratedDocumentResponse])
async def list_employee_documents(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all generated documents for an employee."""
    return get_documents_by_employee(db, employee_id)


@router.get("/{document_id}", response_model=GeneratedDocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single document by ID."""
    doc = get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{document_id}", response_model=GeneratedDocumentResponse)
async def update_document(
    document_id: int,
    payload: DocumentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update document content (for manual edits)."""
    doc = update_document_content(db, document_id, payload.content)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download document as a text/markdown file."""
    doc = get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    from fastapi.responses import Response

    filename = f"{doc.document_type}_{doc.employee_id}_v{doc.version}.md"
    return Response(
        content=doc.content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
