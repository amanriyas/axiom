# app/prompts/__init__.py
"""Prompt templates for LLM-powered onboarding document generation."""

from app.prompts.templates import (
    SYSTEM_PROMPT,
    WELCOME_EMAIL_PROMPT,
    OFFER_LETTER_PROMPT,
    PLAN_30_60_90_PROMPT,
    EQUIPMENT_REQUEST_PROMPT,
    PARSE_DATA_PROMPT,
)

__all__ = [
    "SYSTEM_PROMPT",
    "WELCOME_EMAIL_PROMPT",
    "OFFER_LETTER_PROMPT",
    "PLAN_30_60_90_PROMPT",
    "EQUIPMENT_REQUEST_PROMPT",
    "PARSE_DATA_PROMPT",
]
