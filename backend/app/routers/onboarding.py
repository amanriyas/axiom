# app/routers/onboarding.py
"""Onboarding workflow routes — start, status, SSE stream."""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, User
from app.schemas import (
    OnboardingStartResponse,
    OnboardingWorkflowResponse,
    MessageResponse,
)
from app.services.auth import get_current_user
from app.services.orchestrator import (
    create_workflow,
    get_workflow_by_id,
    get_workflow_by_employee,
    run_workflow,
    run_workflow_stream,
)

router = APIRouter(prefix="/api/onboarding", tags=["Onboarding"])


# ─────────────────────────────────────────────────────────────
# POST /api/onboarding/{employee_id}/start
# ─────────────────────────────────────────────────────────────

@router.post("/{employee_id}/start", response_model=OnboardingStartResponse)
async def start_onboarding(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create and immediately run an onboarding workflow for an employee."""
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check if employee already has an active workflow
    existing = get_workflow_by_employee(db, employee_id)
    if existing and existing.status.value in ("pending", "running"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already has an active onboarding workflow",
        )

    # Create workflow with all steps
    workflow = create_workflow(db, employee_id)

    # Run the workflow in the background (non-blocking)
    asyncio.create_task(_run_workflow_background(db, workflow.id))

    return OnboardingStartResponse(
        workflow_id=workflow.id,
        employee_id=employee_id,
        message="Onboarding workflow started",
    )


async def _run_workflow_background(db: Session, workflow_id: int):
    """Run the workflow asynchronously without blocking the request."""
    try:
        await run_workflow(db, workflow_id)
    except Exception as e:
        print(f"⚠️  Background workflow {workflow_id} error: {e}")


# ─────────────────────────────────────────────────────────────
# GET /api/onboarding/{employee_id}/status
# ─────────────────────────────────────────────────────────────

@router.get("/{employee_id}/status", response_model=OnboardingWorkflowResponse)
async def get_onboarding_status(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current onboarding workflow status for an employee."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    workflow = get_workflow_by_employee(db, employee_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="No onboarding workflow found for this employee")

    return workflow


# ─────────────────────────────────────────────────────────────
# GET /api/onboarding/{employee_id}/stream
# ─────────────────────────────────────────────────────────────

@router.get("/{employee_id}/stream")
async def stream_onboarding(
    employee_id: int,
    db: Session = Depends(get_db),
):
    """
    SSE stream of the onboarding workflow execution.
    
    Creates a new workflow if none exists, or re-streams the latest one.
    NOTE: Auth not enforced on SSE — the frontend handles auth separately.
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Get or create workflow
    workflow = get_workflow_by_employee(db, employee_id)
    if not workflow:
        workflow = create_workflow(db, employee_id)

    async def event_generator():
        async for event_data in run_workflow_stream(db, workflow.id):
            yield f"data: {event_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ─────────────────────────────────────────────────────────────
# GET /api/onboarding/workflow/{workflow_id}
# ─────────────────────────────────────────────────────────────

@router.get("/workflow/{workflow_id}", response_model=OnboardingWorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific workflow by its ID."""
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
