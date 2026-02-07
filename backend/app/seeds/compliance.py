"""Seed compliance tracking data for demo purposes."""

from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models import ComplianceItem, ComplianceStatus, Employee


def seed_compliance(db: Session) -> int:
    """Seed mock compliance items. Returns count created."""
    # Check if compliance items already exist
    existing = db.query(ComplianceItem).first()
    if existing:
        return 0

    # Get employees to attach compliance items to
    employees = db.query(Employee).all()
    if not employees:
        return 0

    today = date.today()
    items_data = []

    # Assign compliance items across available employees
    for i, emp in enumerate(employees):
        if i == 0:
            # Visa expiring soon (30 days)
            items_data.append(dict(
                employee_id=emp.id,
                item_type="visa",
                description=f"H-1B Work Visa — {emp.name}",
                expiry_date=today + timedelta(days=25),
                status=ComplianceStatus.EXPIRING_SOON,
            ))
        elif i == 1:
            # Work permit expiring soon (45 days)
            items_data.append(dict(
                employee_id=emp.id,
                item_type="work_permit",
                description=f"Employment Work Permit — {emp.name}",
                expiry_date=today + timedelta(days=45),
                status=ComplianceStatus.EXPIRING_SOON,
            ))
        elif i == 2:
            # Training certification expired
            items_data.append(dict(
                employee_id=emp.id,
                item_type="certification",
                description=f"SOC 2 Security Compliance Training — {emp.name}",
                expiry_date=today - timedelta(days=15),
                status=ComplianceStatus.EXPIRED,
            ))
        elif i == 3:
            # Equipment return due soon
            items_data.append(dict(
                employee_id=emp.id,
                item_type="equipment",
                description=f"Laptop Return (MacBook Pro) — {emp.name}",
                expiry_date=today + timedelta(days=60),
                status=ComplianceStatus.EXPIRING_SOON,
            ))
        elif i == 4:
            # Valid visa with plenty of time
            items_data.append(dict(
                employee_id=emp.id,
                item_type="visa",
                description=f"Employment Pass — {emp.name}",
                expiry_date=today + timedelta(days=300),
                status=ComplianceStatus.VALID,
            ))
        elif i == 5:
            # Training expiring soon
            items_data.append(dict(
                employee_id=emp.id,
                item_type="training",
                description=f"GDPR Data Handling Certification — {emp.name}",
                expiry_date=today + timedelta(days=20),
                status=ComplianceStatus.EXPIRING_SOON,
            ))
        elif i == 6:
            # Already expired certification
            items_data.append(dict(
                employee_id=emp.id,
                item_type="certification",
                description=f"AWS Cloud Practitioner Certificate — {emp.name}",
                expiry_date=today - timedelta(days=10),
                status=ComplianceStatus.EXPIRED,
            ))
        elif i == 7:
            # Valid training
            items_data.append(dict(
                employee_id=emp.id,
                item_type="training",
                description=f"Anti-Harassment Training Completion — {emp.name}",
                expiry_date=today + timedelta(days=180),
                status=ComplianceStatus.VALID,
            ))

    count = 0
    for item_data in items_data:
        item = ComplianceItem(**item_data)
        db.add(item)
        count += 1

    db.commit()
    return count
