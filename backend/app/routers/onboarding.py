# app/routers/onboarding.py
"""Onboarding workflow routes — start, status, SSE stream."""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import Employee, User
from app.schemas import (
    OnboardingStartResponse,
    OnboardingWorkflowResponse,
    MessageResponse,
)
from app.services.auth import get_current_user, verify_token_string
from app.services.orchestrator import (
    create_workflow,
    get_workflow_by_id,
    get_workflow_by_employee,
    pause_workflow,
    resume_workflow,
    retry_workflow,
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
    asyncio.create_task(_run_workflow_background(workflow.id))

    return OnboardingStartResponse(
        workflow_id=workflow.id,
        employee_id=employee_id,
        message="Onboarding workflow started",
    )


async def _run_workflow_background(workflow_id: int):
    """Run the workflow asynchronously with its own DB session."""
    db = SessionLocal()
    try:
        await run_workflow(db, workflow_id)
    except Exception as e:
        print(f"⚠️  Background workflow {workflow_id} error: {e}")
    finally:
        db.close()


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
    token: str = Query(..., description="JWT token for authentication"),
    db: Session = Depends(get_db),
):
    """
    SSE stream of the onboarding workflow execution.
    
    Auth is enforced via a `token` query parameter (since EventSource
    does not support Authorization headers).
    """
    # Validate the JWT token
    user = verify_token_string(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Get or create workflow
    workflow = get_workflow_by_employee(db, employee_id)
    if not workflow:
        workflow = create_workflow(db, employee_id)

    workflow_id = workflow.id  # Capture ID before request session closes

    async def event_generator():
        # Create a fresh DB session for the long-lived SSE stream
        stream_db = SessionLocal()
        try:
            async for event_data in run_workflow_stream(stream_db, workflow_id):
                yield f"data: {event_data}\n\n"
        finally:
            stream_db.close()

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


# ───────────────────────────────────────────────────────────────
# POST /api/onboarding/{employee_id}/pause
# ───────────────────────────────────────────────────────────────

@router.post("/{employee_id}/pause", response_model=MessageResponse)
async def pause_onboarding(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Pause a running onboarding workflow."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        pause_workflow(db, employee_id)
        return MessageResponse(message="Workflow paused")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ───────────────────────────────────────────────────────────────
# POST /api/onboarding/{employee_id}/resume
# ───────────────────────────────────────────────────────────────

@router.post("/{employee_id}/resume", response_model=OnboardingStartResponse)
async def resume_onboarding(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resume a paused or approval-waiting workflow and continue remaining steps."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        workflow = resume_workflow(db, employee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Re-run the workflow in background — it will skip completed steps
    asyncio.create_task(_run_workflow_background(workflow.id))

    return OnboardingStartResponse(
        workflow_id=workflow.id,
        employee_id=employee_id,
        message="Workflow resumed — executing remaining steps",
    )


# ───────────────────────────────────────────────────────────────
# POST /api/onboarding/{employee_id}/retry
# ───────────────────────────────────────────────────────────────

@router.post("/{employee_id}/retry", response_model=OnboardingStartResponse)
async def retry_onboarding(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retry a failed onboarding workflow — resets failed steps and re-runs."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        workflow = retry_workflow(db, employee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Re-run the workflow in the background (picks up from failed steps)
    asyncio.create_task(_run_workflow_background(workflow.id))

    return OnboardingStartResponse(
        workflow_id=workflow.id,
        employee_id=employee_id,
        message="Retrying failed steps",
    )


# ───────────────────────────────────────────────────────────────
# GET /api/onboarding/templates
# ───────────────────────────────────────────────────────────────

@router.get("/templates")
async def get_templates(
    current_user: User = Depends(get_current_user),
):
    """Return current prompt templates (defaults + any user overrides)."""
    from app.prompts import get_template
    template_keys = ["welcome_email", "offer_letter", "plan_30_60_90", "equipment_request"]
    return {key: get_template(key) for key in template_keys}


# ───────────────────────────────────────────────────────────────
# PUT /api/onboarding/templates
# ───────────────────────────────────────────────────────────────

@router.put("/templates")
async def update_templates(
    templates: dict[str, str],
    current_user: User = Depends(get_current_user),
):
    """Save prompt template overrides. Keys: welcome_email, offer_letter, plan_30_60_90, equipment_request."""
    from app.prompts import set_all_overrides
    valid_keys = {"welcome_email", "offer_letter", "plan_30_60_90", "equipment_request"}
    filtered = {k: v for k, v in templates.items() if k in valid_keys and v.strip()}
    set_all_overrides(filtered)
    return {"message": "Templates updated", "count": len(filtered)}


# ───────────────────────────────────────────────────────────────
# GET /api/onboarding/{employee_id}/export
# ───────────────────────────────────────────────────────────────

@router.get("/{employee_id}/export")
async def export_onboarding_report(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export the onboarding workflow as a downloadable Markdown report."""
    import json as _json

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    workflow = get_workflow_by_employee(db, employee_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="No workflow found")

    # Build Markdown report
    lines: list[str] = []
    lines.append(f"# Onboarding Report — {employee.name}")
    lines.append("")
    lines.append(f"**Email:** {employee.email}  ")
    lines.append(f"**Role:** {employee.role}  ")
    lines.append(f"**Department:** {employee.department}  ")
    lines.append(f"**Start Date:** {employee.start_date}  ")
    lines.append(f"**Manager:** {employee.manager_email or 'N/A'}  ")
    lines.append(f"**Buddy:** {employee.buddy_email or 'N/A'}  ")
    lines.append("")
    lines.append(f"**Workflow Status:** {workflow.status.value.upper()}  ")
    if workflow.started_at:
        lines.append(f"**Started:** {workflow.started_at.strftime('%Y-%m-%d %H:%M')}  ")
    if workflow.completed_at:
        lines.append(f"**Completed:** {workflow.completed_at.strftime('%Y-%m-%d %H:%M')}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    for step in workflow.steps:
        step_label = step.step_type.value.replace("_", " ").title()
        status_emoji = {
            "completed": "✅",
            "failed": "❌",
            "running": "⏳",
            "pending": "⏸️",
            "skipped": "⏭️",
        }.get(step.status.value, "•")

        lines.append(f"## {status_emoji} Step {step.step_order}: {step_label}")
        lines.append("")
        lines.append(f"**Status:** {step.status.value}  ")
        if step.started_at:
            lines.append(f"**Started:** {step.started_at.strftime('%Y-%m-%d %H:%M')}  ")
        if step.completed_at:
            lines.append(f"**Completed:** {step.completed_at.strftime('%Y-%m-%d %H:%M')}  ")
        lines.append("")

        if step.result:
            try:
                data = _json.loads(step.result)
                content = data.get("content") or data.get("ai_summary") or _json.dumps(data, indent=2)
            except (_json.JSONDecodeError, TypeError):
                content = step.result
            lines.append("### Output")
            lines.append("")
            lines.append(content)
            lines.append("")

        if step.error_message:
            lines.append("### Error")
            lines.append("")
            lines.append(f"```\n{step.error_message}\n```")
            lines.append("")

        lines.append("---")
        lines.append("")

    report_text = "\n".join(lines)
    safe_name = employee.name.replace(" ", "_").lower()
    filename = f"onboarding_report_{safe_name}.md"

    return Response(
        content=report_text,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
