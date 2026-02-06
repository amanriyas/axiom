# app/services/calendar.py
"""Google Calendar integration — OAuth + event scheduling with mock fallback."""

import uuid
from datetime import date, timedelta
from typing import Optional

from app.config import settings


def schedule_event(
    title: str,
    event_date: date,
    duration_minutes: int = 60,
    description: str = "",
    attendees: Optional[list[str]] = None,
) -> dict:
    """
    Schedule a Google Calendar event.
    
    Falls back to mock mode when Google credentials are not configured.
    Returns a dict with event details.
    """
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        return _schedule_google_event(title, event_date, duration_minutes, description, attendees)
    else:
        return _mock_schedule_event(title, event_date, duration_minutes, description, attendees)


def schedule_onboarding_events(
    employee_name: str,
    employee_email: str,
    start_date: date,
    manager_email: Optional[str] = None,
    buddy_email: Optional[str] = None,
) -> list[dict]:
    """
    Schedule all standard onboarding events for a new employee.
    
    Events:
      1. Orientation — day 1
      2. Manager 1:1 — day 2
      3. Buddy Meetup — day 3
    """
    events = []

    # 1. Orientation on start date
    events.append(schedule_event(
        title=f"Orientation - {employee_name}",
        event_date=start_date,
        duration_minutes=120,
        description=f"Welcome orientation for {employee_name}",
        attendees=[employee_email] + ([manager_email] if manager_email else []),
    ))

    # 2. Manager 1:1 on day 2
    events.append(schedule_event(
        title=f"Manager 1:1 - {employee_name}",
        event_date=start_date + timedelta(days=1),
        duration_minutes=60,
        description=f"Initial 1:1 meeting between {employee_name} and manager",
        attendees=[employee_email] + ([manager_email] if manager_email else []),
    ))

    # 3. Buddy meetup on day 3
    events.append(schedule_event(
        title=f"Buddy Meetup - {employee_name}",
        event_date=start_date + timedelta(days=2),
        duration_minutes=45,
        description=f"Casual meetup between {employee_name} and onboarding buddy",
        attendees=[employee_email] + ([buddy_email] if buddy_email else []),
    ))

    return events


# ─────────────────────────────────────────────────────────────
# Google Calendar API implementation
# ─────────────────────────────────────────────────────────────

def _schedule_google_event(
    title: str,
    event_date: date,
    duration_minutes: int,
    description: str,
    attendees: Optional[list[str]],
) -> dict:
    """
    Create a real Google Calendar event.
    
    Requires valid Google OAuth credentials.
    """
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        # NOTE: In a production app, you would store and retrieve
        # user-specific OAuth tokens from the database.
        # For the hackathon, this is a placeholder.
        raise NotImplementedError("Google Calendar OAuth flow not yet configured")

    except (ImportError, NotImplementedError):
        # Fall back to mock
        return _mock_schedule_event(title, event_date, duration_minutes, description, attendees)


# ─────────────────────────────────────────────────────────────
# Mock implementation (for demos / no Google credentials)
# ─────────────────────────────────────────────────────────────

def _mock_schedule_event(
    title: str,
    event_date: date,
    duration_minutes: int,
    description: str,
    attendees: Optional[list[str]],
) -> dict:
    """Return a mock calendar event for demo/testing."""
    return {
        "id": f"mock_{uuid.uuid4().hex[:12]}",
        "title": title,
        "date": event_date.isoformat(),
        "duration_minutes": duration_minutes,
        "description": description,
        "attendees": attendees or [],
        "status": "mock",
        "message": "Mock event — Google Calendar not configured",
    }
