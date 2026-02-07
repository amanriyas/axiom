# app/services/document_generator.py
"""Document generation service — creates jurisdiction-aware legal documents using LLM + RAG."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models import Employee, GeneratedDocument, DocumentStatus, JurisdictionTemplate
from app.services import llm, rag
from app.prompts.documents import (
    EMPLOYMENT_CONTRACT_PROMPT,
    NDA_PROMPT,
    EQUITY_AGREEMENT_PROMPT,
    OFFER_LETTER_DOCUMENT_PROMPT,
)


def _get_jurisdiction_template(db: Session, jurisdiction: str, document_type: str) -> Optional[str]:
    """Fetch the jurisdiction-specific template content."""
    template = (
        db.query(JurisdictionTemplate)
        .filter(
            JurisdictionTemplate.jurisdiction_code == jurisdiction.upper(),
            JurisdictionTemplate.document_type == document_type,
        )
        .first()
    )
    return template.template_content if template else None


def _get_legal_requirements(db: Session, jurisdiction: str, document_type: str) -> Optional[str]:
    """Fetch legal requirements for a jurisdiction + document type."""
    template = (
        db.query(JurisdictionTemplate)
        .filter(
            JurisdictionTemplate.jurisdiction_code == jurisdiction.upper(),
            JurisdictionTemplate.document_type == document_type,
        )
        .first()
    )
    return template.legal_requirements if template else None


async def generate_employment_contract(db: Session, employee: Employee) -> GeneratedDocument:
    """Generate an employment contract using jurisdiction template + LLM + RAG."""
    jurisdiction = employee.jurisdiction or "US"
    template = _get_jurisdiction_template(db, jurisdiction, "employment_contract")
    legal_reqs = _get_legal_requirements(db, jurisdiction, "employment_contract")

    # Get policy context from RAG
    context_results = rag.query_policies("employment contract terms conditions onboarding")
    context = "\n".join([r["text"] for r in context_results])

    prompt = EMPLOYMENT_CONTRACT_PROMPT.format(
        name=employee.name,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
        manager_email=employee.manager_email or "TBD",
        jurisdiction=jurisdiction,
        jurisdiction_template=template or "No jurisdiction template available. Use standard terms.",
        legal_requirements=legal_reqs or "[]",
    )

    content = await llm.generate_text(prompt=prompt, context=context)

    doc = GeneratedDocument(
        employee_id=employee.id,
        document_type="employment_contract",
        jurisdiction=jurisdiction,
        content=content,
        status=DocumentStatus.DRAFT,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


async def generate_nda(db: Session, employee: Employee) -> GeneratedDocument:
    """Generate an NDA using jurisdiction template + LLM + RAG."""
    jurisdiction = employee.jurisdiction or "US"
    template = _get_jurisdiction_template(db, jurisdiction, "nda")
    legal_reqs = _get_legal_requirements(db, jurisdiction, "nda")

    context_results = rag.query_policies("non-disclosure agreement confidentiality intellectual property")
    context = "\n".join([r["text"] for r in context_results])

    prompt = NDA_PROMPT.format(
        name=employee.name,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
        jurisdiction=jurisdiction,
        jurisdiction_template=template or "No jurisdiction template available. Use standard terms.",
        legal_requirements=legal_reqs or "[]",
    )

    content = await llm.generate_text(prompt=prompt, context=context)

    doc = GeneratedDocument(
        employee_id=employee.id,
        document_type="nda",
        jurisdiction=jurisdiction,
        content=content,
        status=DocumentStatus.DRAFT,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


async def generate_equity_agreement(db: Session, employee: Employee) -> GeneratedDocument:
    """Generate an equity/stock agreement using LLM + RAG."""
    jurisdiction = employee.jurisdiction or "US"

    context_results = rag.query_policies("equity stock options vesting compensation")
    context = "\n".join([r["text"] for r in context_results])

    prompt = EQUITY_AGREEMENT_PROMPT.format(
        name=employee.name,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
        jurisdiction=jurisdiction,
    )

    content = await llm.generate_text(prompt=prompt, context=context)

    doc = GeneratedDocument(
        employee_id=employee.id,
        document_type="equity_agreement",
        jurisdiction=jurisdiction,
        content=content,
        status=DocumentStatus.DRAFT,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


async def generate_offer_letter_doc(db: Session, employee: Employee) -> GeneratedDocument:
    """Generate a formal offer letter document using jurisdiction template + LLM + RAG."""
    jurisdiction = employee.jurisdiction or "US"
    template = _get_jurisdiction_template(db, jurisdiction, "offer_letter")
    legal_reqs = _get_legal_requirements(db, jurisdiction, "offer_letter")

    context_results = rag.query_policies("offer letter employment terms compensation benefits")
    context = "\n".join([r["text"] for r in context_results])

    prompt = OFFER_LETTER_DOCUMENT_PROMPT.format(
        name=employee.name,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
        manager_email=employee.manager_email or "TBD",
        jurisdiction=jurisdiction,
        jurisdiction_template=template or "No jurisdiction template available. Use standard terms.",
        legal_requirements=legal_reqs or "[]",
    )

    content = await llm.generate_text(prompt=prompt, context=context)

    doc = GeneratedDocument(
        employee_id=employee.id,
        document_type="offer_letter",
        jurisdiction=jurisdiction,
        content=content,
        status=DocumentStatus.DRAFT,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_documents_by_employee(db: Session, employee_id: int) -> list[GeneratedDocument]:
    """Get all generated documents for an employee."""
    return (
        db.query(GeneratedDocument)
        .filter(GeneratedDocument.employee_id == employee_id)
        .order_by(GeneratedDocument.generated_at.desc())
        .all()
    )


def get_document_by_id(db: Session, document_id: int) -> Optional[GeneratedDocument]:
    """Get a single document by ID."""
    return db.query(GeneratedDocument).filter(GeneratedDocument.id == document_id).first()


def update_document_content(db: Session, document_id: int, content: str) -> Optional[GeneratedDocument]:
    """Update document content (for manual edits)."""
    doc = get_document_by_id(db, document_id)
    if not doc:
        return None
    doc.content = content
    doc.version += 1
    db.commit()
    db.refresh(doc)
    return doc
