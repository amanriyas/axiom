# app/services/employee.py
"""Employee CRUD operations and CSV bulk import."""

import csv
import io
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Employee, EmployeeStatus
from app.schemas import EmployeeCreate, EmployeeUpdate


def get_all_employees(db: Session) -> list[Employee]:
    """Return all employees ordered by creation date descending."""
    return db.query(Employee).order_by(Employee.created_at.desc()).all()


def get_employee_by_id(db: Session, employee_id: int) -> Optional[Employee]:
    """Fetch a single employee by ID."""
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
    """Fetch a single employee by email."""
    return db.query(Employee).filter(Employee.email == email).first()


def create_employee(db: Session, payload: EmployeeCreate) -> Employee:
    """Create a new employee record."""
    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(db: Session, employee_id: int, payload: EmployeeUpdate) -> Optional[Employee]:
    """Update an existing employee. Returns None if not found."""
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee_id: int) -> bool:
    """Delete an employee. Returns True if deleted, False if not found."""
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        return False
    db.delete(employee)
    db.commit()
    return True


def bulk_import_csv(db: Session, file_content: bytes) -> dict:
    """
    Parse a CSV file and create employees in bulk.

    Expected CSV columns:
        name, email, role, department, start_date, manager_email, buddy_email

    Returns dict with { total, created, errors }.
    """
    errors: list[str] = []
    created = 0

    try:
        text = file_content.decode("utf-8")
    except UnicodeDecodeError:
        text = file_content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    for i, row in enumerate(rows, start=2):  # row 1 is header
        try:
            # Normalise column names (strip whitespace, lowercase)
            row = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in row.items() if k}

            name = row.get("name", "")
            email = row.get("email", "")
            role = row.get("role", "")
            department = row.get("department", "")
            start_date_str = row.get("start_date", "")
            manager_email = row.get("manager_email") or None
            buddy_email = row.get("buddy_email") or None

            if not all([name, email, role, department, start_date_str]):
                errors.append(f"Row {i}: Missing required fields")
                continue

            # Parse date (supports YYYY-MM-DD and MM/DD/YYYY)
            try:
                start_date = date.fromisoformat(start_date_str)
            except ValueError:
                try:
                    parts = start_date_str.split("/")
                    start_date = date(int(parts[2]), int(parts[0]), int(parts[1]))
                except (ValueError, IndexError):
                    errors.append(f"Row {i}: Invalid date format '{start_date_str}'")
                    continue

            # Skip duplicates
            existing = get_employee_by_email(db, email)
            if existing:
                errors.append(f"Row {i}: Email '{email}' already exists")
                continue

            employee = Employee(
                name=name,
                email=email,
                role=role,
                department=department,
                start_date=start_date,
                manager_email=manager_email,
                buddy_email=buddy_email,
            )
            db.add(employee)
            created += 1

        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    if created > 0:
        db.commit()

    return {"total": len(rows), "created": created, "errors": errors}
