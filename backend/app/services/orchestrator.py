# app/services/orchestrator.py
"""Workflow orchestration engine — manages the 6-step onboarding pipeline."""

import json
from datetime import datetime
from typing import Optional, AsyncGenerator

from sqlalchemy.orm import Session

from app.models import (
    Employee,
    EmployeeStatus,
    OnboardingWorkflow,
    OnboardingStep,
    StepType,
    StepStatus,
    WorkflowStatus,
)
from app.services import llm, rag


# ─────────────────────────────────────────────────────────────
# Step definitions (order matters)
# ─────────────────────────────────────────────────────────────

STEP_ORDER = [
    StepType.PARSE_DATA,
    StepType.WELCOME_EMAIL,
    StepType.OFFER_LETTER,
    StepType.PLAN_30_60_90,
    StepType.SCHEDULE_EVENTS,
    StepType.EQUIPMENT_REQUEST,
]


# ─────────────────────────────────────────────────────────────
# Workflow creation
# ─────────────────────────────────────────────────────────────

def create_workflow(db: Session, employee_id: int) -> OnboardingWorkflow:
    """Create a new onboarding workflow with all steps initialized as PENDING."""
    workflow = OnboardingWorkflow(employee_id=employee_id)
    db.add(workflow)
    db.flush()  # Get workflow.id

    # Create all steps in order
    for order, step_type in enumerate(STEP_ORDER, start=1):
        step = OnboardingStep(
            workflow_id=workflow.id,
            step_type=step_type,
            step_order=order,
            status=StepStatus.PENDING,
        )
        db.add(step)

    db.commit()
    db.refresh(workflow)
    return workflow


def get_workflow_by_id(db: Session, workflow_id: int) -> Optional[OnboardingWorkflow]:
    """Fetch a workflow by ID."""
    return db.query(OnboardingWorkflow).filter(OnboardingWorkflow.id == workflow_id).first()


def get_workflow_by_employee(db: Session, employee_id: int) -> Optional[OnboardingWorkflow]:
    """Fetch the most recent workflow for an employee."""
    return (
        db.query(OnboardingWorkflow)
        .filter(OnboardingWorkflow.employee_id == employee_id)
        .order_by(OnboardingWorkflow.created_at.desc())
        .first()
    )


# ─────────────────────────────────────────────────────────────
# Step execution logic
# ─────────────────────────────────────────────────────────────

async def execute_step(db: Session, step: OnboardingStep, employee: Employee) -> str:
    """Execute a single workflow step and return the result."""
    step_type = step.step_type

    if step_type == StepType.PARSE_DATA:
        return await _step_parse_data(employee)
    elif step_type == StepType.WELCOME_EMAIL:
        return await _step_welcome_email(employee)
    elif step_type == StepType.OFFER_LETTER:
        return await _step_offer_letter(employee)
    elif step_type == StepType.PLAN_30_60_90:
        return await _step_30_60_90_plan(employee)
    elif step_type == StepType.SCHEDULE_EVENTS:
        return await _step_schedule_events(employee)
    elif step_type == StepType.EQUIPMENT_REQUEST:
        return await _step_equipment_request(employee)
    else:
        return f"Unknown step type: {step_type}"


async def _step_parse_data(employee: Employee) -> str:
    """Step 1: Parse and validate employee data."""
    data = {
        "employee_name": employee.name,
        "email": employee.email,
        "role": employee.role,
        "department": employee.department,
        "start_date": employee.start_date.isoformat(),
        "manager_email": employee.manager_email,
        "buddy_email": employee.buddy_email,
    }
    return json.dumps({"parsed_data": data, "validation": "passed"})


async def _step_welcome_email(employee: Employee) -> str:
    """Step 2: Generate welcome email using LLM."""
    context_results = rag.query_policies("onboarding welcome email company culture")
    context = "\n".join([r["text"] for r in context_results])

    prompt = f"""Generate a warm, professional welcome email for a new employee:
    
Name: {employee.name}
Role: {employee.role}
Department: {employee.department}
Start Date: {employee.start_date}
Manager: {employee.manager_email or 'TBD'}
Buddy: {employee.buddy_email or 'TBD'}

The email should welcome them, outline what to expect on day one, and express excitement about them joining."""

    email_content = await llm.generate_text(prompt=prompt, context=context)
    return json.dumps({"type": "welcome_email", "content": email_content})


async def _step_offer_letter(employee: Employee) -> str:
    """Step 3: Generate offer letter using LLM + RAG."""
    context_results = rag.query_policies("offer letter employment terms compensation")
    context = "\n".join([r["text"] for r in context_results])

    prompt = f"""Generate a professional offer letter for:

Name: {employee.name}
Role: {employee.role}
Department: {employee.department}
Start Date: {employee.start_date}

Include standard offer letter sections: position details, compensation placeholder, benefits summary, and acceptance instructions."""

    letter_content = await llm.generate_text(prompt=prompt, context=context)
    return json.dumps({"type": "offer_letter", "content": letter_content})


async def _step_30_60_90_plan(employee: Employee) -> str:
    """Step 4: Generate 30-60-90 day plan using LLM + RAG."""
    context_results = rag.query_policies("onboarding plan training milestones")
    context = "\n".join([r["text"] for r in context_results])

    prompt = f"""Create a comprehensive 30-60-90 day onboarding plan for:

Name: {employee.name}
Role: {employee.role}
Department: {employee.department}

Structure it as:
- First 30 Days: Learning & Orientation
- Days 31-60: Contributing & Collaborating  
- Days 61-90: Leading & Delivering

Include specific goals and milestones for each phase."""

    plan_content = await llm.generate_text(prompt=prompt, context=context)
    return json.dumps({"type": "30_60_90_plan", "content": plan_content})


async def _step_schedule_events(employee: Employee) -> str:
    """Step 5: Schedule calendar events (mock implementation)."""
    # This would integrate with the calendar service
    events = [
        {"type": "orientation", "title": f"Orientation - {employee.name}", "scheduled": True},
        {"type": "manager_1on1", "title": f"1:1 with Manager - {employee.name}", "scheduled": True},
        {"type": "buddy_meetup", "title": f"Buddy Meetup - {employee.name}", "scheduled": True},
    ]
    return json.dumps({"type": "calendar_events", "events": events})


async def _step_equipment_request(employee: Employee) -> str:
    """Step 6: Generate equipment request using LLM."""
    prompt = f"""Generate an IT equipment provisioning request for:

Name: {employee.name}
Role: {employee.role}
Department: {employee.department}
Start Date: {employee.start_date}

Include standard equipment (laptop, monitor, peripherals) and software licenses needed for their role."""

    request_content = await llm.generate_text(prompt=prompt)
    return json.dumps({"type": "equipment_request", "content": request_content})


# ─────────────────────────────────────────────────────────────
# Workflow execution
# ─────────────────────────────────────────────────────────────

async def run_workflow(db: Session, workflow_id: int) -> OnboardingWorkflow:
    """Execute all steps of a workflow sequentially."""
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise ValueError(f"Workflow {workflow_id} not found")

    employee = workflow.employee

    # Mark workflow as running
    workflow.status = WorkflowStatus.RUNNING
    workflow.started_at = datetime.utcnow()
    employee.status = EmployeeStatus.ONBOARDING
    db.commit()

    try:
        for step in workflow.steps:
            # Mark step as running
            step.status = StepStatus.RUNNING
            step.started_at = datetime.utcnow()
            db.commit()

            try:
                result = await execute_step(db, step, employee)
                step.status = StepStatus.COMPLETED
                step.result = result
                step.completed_at = datetime.utcnow()
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error_message = str(e)
                step.completed_at = datetime.utcnow()
                raise

            db.commit()

        # All steps completed
        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = datetime.utcnow()
        employee.status = EmployeeStatus.COMPLETED
        db.commit()

    except Exception as e:
        workflow.status = WorkflowStatus.FAILED
        workflow.error_message = str(e)
        workflow.completed_at = datetime.utcnow()
        employee.status = EmployeeStatus.FAILED
        db.commit()

    db.refresh(workflow)
    return workflow


# ─────────────────────────────────────────────────────────────
# Streaming execution (for SSE)
# ─────────────────────────────────────────────────────────────

async def run_workflow_stream(db: Session, workflow_id: int) -> AsyncGenerator[str, None]:
    """
    Execute workflow and yield SSE events for real-time updates.
    
    Yields JSON strings in SSE format for the Agent Thinking Panel.
    """
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        yield _sse_event("error", {"message": f"Workflow {workflow_id} not found"})
        return

    employee = workflow.employee

    # Mark workflow as running
    workflow.status = WorkflowStatus.RUNNING
    workflow.started_at = datetime.utcnow()
    employee.status = EmployeeStatus.ONBOARDING
    db.commit()

    yield _sse_event("workflow_started", {
        "workflow_id": workflow.id,
        "employee_name": employee.name,
    })

    try:
        for step in workflow.steps:
            # Mark step as running
            step.status = StepStatus.RUNNING
            step.started_at = datetime.utcnow()
            db.commit()

            yield _sse_event("step_started", {
                "step_id": step.id,
                "step_type": step.step_type.value,
                "step_order": step.step_order,
            })

            try:
                # Simulate thinking with streaming
                yield _sse_event("thinking", {"message": f"Processing {step.step_type.value}..."})

                result = await execute_step(db, step, employee)
                step.status = StepStatus.COMPLETED
                step.result = result
                step.completed_at = datetime.utcnow()
                db.commit()

                yield _sse_event("step_completed", {
                    "step_id": step.id,
                    "step_type": step.step_type.value,
                    "result_preview": result[:200] if result else None,
                })

            except Exception as e:
                step.status = StepStatus.FAILED
                step.error_message = str(e)
                step.completed_at = datetime.utcnow()
                db.commit()

                yield _sse_event("step_failed", {
                    "step_id": step.id,
                    "step_type": step.step_type.value,
                    "error": str(e),
                })
                raise

        # All steps completed
        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = datetime.utcnow()
        employee.status = EmployeeStatus.COMPLETED
        db.commit()

        yield _sse_event("workflow_completed", {
            "workflow_id": workflow.id,
            "total_steps": len(workflow.steps),
        })

    except Exception as e:
        workflow.status = WorkflowStatus.FAILED
        workflow.error_message = str(e)
        workflow.completed_at = datetime.utcnow()
        employee.status = EmployeeStatus.FAILED
        db.commit()

        yield _sse_event("workflow_failed", {
            "workflow_id": workflow.id,
            "error": str(e),
        })


def _sse_event(event_type: str, data: dict) -> str:
    """Format an SSE event."""
    return json.dumps({"event": event_type, "data": data})
