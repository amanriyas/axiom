# app/routers/jurisdictions.py
"""Jurisdiction routes — list jurisdictions and their templates."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JurisdictionTemplate, User
from app.schemas import JurisdictionInfo, JurisdictionTemplateResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/jurisdictions", tags=["Jurisdictions"])


@router.get("/", response_model=list[JurisdictionInfo])
async def list_jurisdictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all available jurisdictions with their document types."""
    templates = db.query(JurisdictionTemplate).all()

    # Group by jurisdiction code
    jurisdictions: dict[str, JurisdictionInfo] = {}
    for t in templates:
        if t.jurisdiction_code not in jurisdictions:
            jurisdictions[t.jurisdiction_code] = JurisdictionInfo(
                code=t.jurisdiction_code,
                name=t.jurisdiction_name,
                document_types=[],
            )
        jurisdictions[t.jurisdiction_code].document_types.append(t.document_type)

    # If no templates exist yet, return default jurisdictions
    if not jurisdictions:
        return [
            JurisdictionInfo(code="US", name="United States", document_types=[]),
            JurisdictionInfo(code="UK", name="United Kingdom", document_types=[]),
            JurisdictionInfo(code="AE", name="United Arab Emirates", document_types=[]),
        ]

    return list(jurisdictions.values())


@router.get("/{code}", response_model=JurisdictionInfo)
async def get_jurisdiction(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details for a specific jurisdiction."""
    templates = (
        db.query(JurisdictionTemplate)
        .filter(JurisdictionTemplate.jurisdiction_code == code.upper())
        .all()
    )

    if not templates:
        raise HTTPException(status_code=404, detail=f"Jurisdiction '{code}' not found")

    return JurisdictionInfo(
        code=templates[0].jurisdiction_code,
        name=templates[0].jurisdiction_name,
        document_types=[t.document_type for t in templates],
    )


@router.get("/{code}/templates", response_model=list[JurisdictionTemplateResponse])
async def get_jurisdiction_templates(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all document templates for a specific jurisdiction."""
    templates = (
        db.query(JurisdictionTemplate)
        .filter(JurisdictionTemplate.jurisdiction_code == code.upper())
        .all()
    )

    if not templates:
        raise HTTPException(status_code=404, detail=f"No templates found for jurisdiction '{code}'")

    return templates
