# app/routers/employees.py
"""Employee management routes — CRUD + CSV bulk import."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    MessageResponse,
    BulkUploadResponse,
)
from app.services import employee as employee_service
from app.services.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/api/employees", tags=["Employees"])


# ─────────────────────────────────────────────────────────────
# GET /api/employees/
# ─────────────────────────────────────────────────────────────

@router.get("/", response_model=list[EmployeeResponse])
async def list_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all employees."""
    return employee_service.get_all_employees(db)


# ─────────────────────────────────────────────────────────────
# POST /api/employees/
# ─────────────────────────────────────────────────────────────

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a single employee."""
    existing = employee_service.get_employee_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists",
        )
    return employee_service.create_employee(db, payload)


# ─────────────────────────────────────────────────────────────
# GET /api/employees/{id}
# ─────────────────────────────────────────────────────────────

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a single employee by ID."""
    employee = employee_service.get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


# ─────────────────────────────────────────────────────────────
# PUT /api/employees/{id}
# ─────────────────────────────────────────────────────────────

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing employee."""
    employee = employee_service.update_employee(db, employee_id, payload)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


# ─────────────────────────────────────────────────────────────
# DELETE /api/employees/{id}
# ─────────────────────────────────────────────────────────────

@router.delete("/{employee_id}", response_model=MessageResponse)
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an employee."""
    deleted = employee_service.delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    return MessageResponse(message="Employee deleted successfully")


# ─────────────────────────────────────────────────────────────
# POST /api/employees/upload
# ─────────────────────────────────────────────────────────────

@router.post("/upload", response_model=BulkUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk import employees from a CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted",
        )

    content = await file.read()
    result = employee_service.bulk_import_csv(db, content)
    return BulkUploadResponse(**result)
