# app/prompts/documents/__init__.py
"""Document-specific prompt templates for jurisdiction-aware generation."""

from app.prompts.documents.employment_contract import EMPLOYMENT_CONTRACT_PROMPT
from app.prompts.documents.nda import NDA_PROMPT
from app.prompts.documents.equity_agreement import EQUITY_AGREEMENT_PROMPT
from app.prompts.documents.offer_letter import OFFER_LETTER_DOCUMENT_PROMPT

__all__ = [
    "EMPLOYMENT_CONTRACT_PROMPT",
    "NDA_PROMPT",
    "EQUITY_AGREEMENT_PROMPT",
    "OFFER_LETTER_DOCUMENT_PROMPT",
]
