# app/routers/calendar.py
"""Calendar routes — schedule events, list mock/real events."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, User
from app.schemas import CalendarEventCreate, CalendarEventResponse, MessageResponse
from app.services.auth import get_current_user
from app.services.calendar import schedule_event, schedule_onboarding_events

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


# ─────────────────────────────────────────────────────────────
# POST /api/calendar/schedule
# ─────────────────────────────────────────────────────────────

@router.post("/schedule", response_model=CalendarEventResponse)
async def create_event(
    payload: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule a single calendar event."""
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    result = schedule_event(
        title=payload.title,
        event_date=payload.date,
        duration_minutes=payload.duration_minutes,
        description=payload.description or "",
        attendees=payload.attendees,
    )

    return CalendarEventResponse(
        id=result["id"],
        title=result["title"],
        date=payload.date,
        status=result["status"],
    )


# ─────────────────────────────────────────────────────────────
# POST /api/calendar/schedule-all/{employee_id}
# ─────────────────────────────────────────────────────────────

@router.post("/schedule-all/{employee_id}")
async def schedule_all_events(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule all standard onboarding events for an employee."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    events = schedule_onboarding_events(
        employee_name=employee.name,
        employee_email=employee.email,
        start_date=employee.start_date,
        manager_email=employee.manager_email,
        buddy_email=employee.buddy_email,
    )

    return {
        "employee_id": employee_id,
        "events_scheduled": len(events),
        "events": events,
    }
