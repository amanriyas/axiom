# app/routers/compliance.py
"""Compliance tracking routes — monitor expirations and alerts."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import ComplianceItemCreate, ComplianceItemResponse, ComplianceSummary
from app.services.auth import get_current_user
from app.services.compliance import (
    get_all_items,
    get_expiring_soon,
    get_expired,
    get_by_employee,
    create_item,
    get_summary,
    generate_predictive_alert,
)

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


@router.get("/")
async def list_compliance_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all compliance items with enriched data."""
    return get_all_items(db)


@router.get("/summary", response_model=ComplianceSummary)
async def compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance summary counts."""
    return get_summary(db)


@router.get("/alerts")
async def compliance_alerts(
    days: int = 60,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get items expiring within specified days."""
    return get_expiring_soon(db, days=days)


@router.get("/expired")
async def expired_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get expired compliance items."""
    return get_expired(db)


@router.get("/predictions")
async def predictive_alerts(
    current_user: User = Depends(get_current_user),
):
    """Get AI-generated predictive compliance alerts."""
    return generate_predictive_alert()


@router.get("/employee/{employee_id}")
async def employee_compliance(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance items for a specific employee."""
    return get_by_employee(db, employee_id)


@router.post("/", response_model=ComplianceItemResponse)
async def add_compliance_item(
    payload: ComplianceItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new compliance tracking item."""
    from app.models import Employee

    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    item = create_item(db, payload)

    return {
        **{
            "id": item.id,
            "employee_id": item.employee_id,
            "item_type": item.item_type,
            "description": item.description,
            "expiry_date": item.expiry_date,
            "status": item.status.value,
            "reminder_sent": item.reminder_sent,
            "created_at": item.created_at,
        },
        "employee_name": employee.name,
        "days_remaining": (item.expiry_date - __import__("datetime").date.today()).days,
    }
