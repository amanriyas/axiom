# app/prompts/__init__.py
"""Prompt templates for LLM-powered onboarding document generation."""

import json
import os
from typing import Optional

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
    "get_template",
    "set_template",
    "get_all_overrides",
    "set_all_overrides",
]

# ── Template override store ──────────────────────────────────
# Overrides are persisted in data/template_overrides.json
# The orchestrator calls get_template(key) which returns the
# override if one exists, otherwise the default from templates.py.

_OVERRIDES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "template_overrides.json",
)

_DEFAULTS: dict[str, str] = {
    "welcome_email": WELCOME_EMAIL_PROMPT,
    "offer_letter": OFFER_LETTER_PROMPT,
    "plan_30_60_90": PLAN_30_60_90_PROMPT,
    "equipment_request": EQUIPMENT_REQUEST_PROMPT,
}


def _load_overrides() -> dict[str, str]:
    """Load template overrides from disk."""
    try:
        with open(_OVERRIDES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_overrides(overrides: dict[str, str]) -> None:
    """Persist template overrides to disk."""
    os.makedirs(os.path.dirname(_OVERRIDES_FILE), exist_ok=True)
    with open(_OVERRIDES_FILE, "w", encoding="utf-8") as f:
        json.dump(overrides, f, indent=2)


def get_template(key: str) -> str:
    """Return the override for *key* if it exists, otherwise the default."""
    overrides = _load_overrides()
    return overrides.get(key, _DEFAULTS.get(key, ""))


def set_template(key: str, prompt: str) -> None:
    """Save a single template override."""
    overrides = _load_overrides()
    overrides[key] = prompt
    _save_overrides(overrides)


def get_all_overrides() -> dict[str, str]:
    """Return the full override dict (only keys that differ from default)."""
    return _load_overrides()


def set_all_overrides(templates: dict[str, str]) -> None:
    """Replace all overrides at once."""
    _save_overrides(templates)
