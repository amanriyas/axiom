# app/services/compliance.py
"""Compliance tracking service — monitors visa, certifications, training expirations."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import ComplianceItem, ComplianceStatus, Employee
from app.schemas import ComplianceItemCreate


def get_all_items(db: Session) -> list[dict]:
    """Get all compliance items with enriched employee info."""
    items = db.query(ComplianceItem).order_by(ComplianceItem.expiry_date.asc()).all()
    return _enrich_items(db, items)


def get_expiring_soon(db: Session, days: int = 60) -> list[dict]:
    """Get items expiring within the specified number of days."""
    cutoff = date.today() + timedelta(days=days)
    items = (
        db.query(ComplianceItem)
        .filter(
            ComplianceItem.expiry_date <= cutoff,
            ComplianceItem.expiry_date >= date.today(),
            ComplianceItem.status != ComplianceStatus.EXPIRED,
        )
        .order_by(ComplianceItem.expiry_date.asc())
        .all()
    )
    return _enrich_items(db, items)


def get_expired(db: Session) -> list[dict]:
    """Get all expired items."""
    items = (
        db.query(ComplianceItem)
        .filter(ComplianceItem.expiry_date < date.today())
        .order_by(ComplianceItem.expiry_date.desc())
        .all()
    )
    # Update status if needed
    for item in items:
        if item.status != ComplianceStatus.EXPIRED:
            item.status = ComplianceStatus.EXPIRED
    db.commit()
    return _enrich_items(db, items)


def get_by_employee(db: Session, employee_id: int) -> list[dict]:
    """Get all compliance items for a specific employee."""
    items = (
        db.query(ComplianceItem)
        .filter(ComplianceItem.employee_id == employee_id)
        .order_by(ComplianceItem.expiry_date.asc())
        .all()
    )
    return _enrich_items(db, items)


def create_item(db: Session, data: ComplianceItemCreate) -> ComplianceItem:
    """Create a new compliance item."""
    today = date.today()
    expiry = data.expiry_date

    # Auto-determine status
    if expiry < today:
        status = ComplianceStatus.EXPIRED
    elif expiry <= today + timedelta(days=60):
        status = ComplianceStatus.EXPIRING_SOON
    else:
        status = ComplianceStatus.VALID

    item = ComplianceItem(
        employee_id=data.employee_id,
        item_type=data.item_type,
        description=data.description,
        expiry_date=data.expiry_date,
        status=status,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_summary(db: Session) -> dict:
    """Get compliance summary counts."""
    all_items = db.query(ComplianceItem).all()

    # Refresh statuses based on current date
    today = date.today()
    for item in all_items:
        if item.expiry_date < today and item.status != ComplianceStatus.EXPIRED:
            item.status = ComplianceStatus.EXPIRED
        elif item.expiry_date <= today + timedelta(days=60) and item.expiry_date >= today:
            if item.status == ComplianceStatus.VALID:
                item.status = ComplianceStatus.EXPIRING_SOON
    db.commit()

    valid = sum(1 for i in all_items if i.status == ComplianceStatus.VALID)
    expiring = sum(1 for i in all_items if i.status == ComplianceStatus.EXPIRING_SOON)
    expired = sum(1 for i in all_items if i.status == ComplianceStatus.EXPIRED)

    return {
        "valid": valid,
        "expiring_soon": expiring,
        "expired": expired,
        "total": len(all_items),
    }


def generate_predictive_alert() -> list[dict]:
    """Generate mock AI predictive compliance alerts as structured data."""
    today = date.today()
    return [
        {
            "employee_id": 0,
            "employee_name": "Q2 2026 Hires (Planned)",
            "item_type": "visa",
            "description": "H-1B Visa Sponsorship — 3 additional sponsorships needed for Q2 engineering hires",
            "expiry_date": (today + timedelta(days=90)).isoformat(),
            "days_remaining": 90,
            "risk_level": "high",
            "recommended_action": "Start visa applications by March 15, 2026 (USCIS H-1B cap season). Budget $12,000–$15,000 per application.",
        },
        {
            "employee_id": 0,
            "employee_name": "Multiple Employees",
            "item_type": "certification",
            "description": "Professional Certifications Expiring — 2 employees have certs expiring within 30 days",
            "expiry_date": (today + timedelta(days=28)).isoformat(),
            "days_remaining": 28,
            "risk_level": "critical",
            "recommended_action": "Schedule renewal exams and notify affected employees immediately.",
        },
        {
            "employee_id": 0,
            "employee_name": "4 Team Members",
            "item_type": "training",
            "description": "SOC 2 Compliance Training — required before Q2 audit deadline",
            "expiry_date": (today + timedelta(days=60)).isoformat(),
            "days_remaining": 60,
            "risk_level": "medium",
            "recommended_action": "Assign SOC 2 training modules and set completion deadline 2 weeks before audit.",
        },
    ]


def _enrich_items(db: Session, items: list[ComplianceItem]) -> list[dict]:
    """Enrich compliance items with employee name and days remaining."""
    today = date.today()
    result = []
    for item in items:
        employee = db.query(Employee).filter(Employee.id == item.employee_id).first()
        days_remaining = (item.expiry_date - today).days

        result.append({
            "id": item.id,
            "employee_id": item.employee_id,
            "item_type": item.item_type,
            "description": item.description,
            "expiry_date": item.expiry_date.isoformat(),
            "status": item.status.value if hasattr(item.status, "value") else item.status,
            "reminder_sent": item.reminder_sent,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "employee_name": employee.name if employee else "Unknown",
            "days_remaining": days_remaining,
        })
    return result
