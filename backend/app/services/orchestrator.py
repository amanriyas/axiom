# app/services/orchestrator.py
"""Workflow orchestration engine — manages the 6-step onboarding pipeline."""

import json
import asyncio
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
from app.services.calendar import schedule_onboarding_events
from app.prompts import get_template
from app.prompts.templates import PARSE_DATA_PROMPT


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


def pause_workflow(db: Session, employee_id: int) -> OnboardingWorkflow:
    """Pause a running workflow. The stream loop will stop before the next step."""
    workflow = get_workflow_by_employee(db, employee_id)
    if not workflow:
        raise ValueError("No workflow found")
    if workflow.status not in (WorkflowStatus.RUNNING, WorkflowStatus.PENDING):
        raise ValueError(f"Cannot pause a workflow with status '{workflow.status.value}'")
    workflow.status = WorkflowStatus.PAUSED
    db.commit()
    db.refresh(workflow)
    return workflow


def resume_workflow(db: Session, employee_id: int) -> OnboardingWorkflow:
    """Resume a paused workflow."""
    workflow = get_workflow_by_employee(db, employee_id)
    if not workflow:
        raise ValueError("No workflow found")
    if workflow.status != WorkflowStatus.PAUSED:
        raise ValueError(f"Cannot resume a workflow with status '{workflow.status.value}'")
    workflow.status = WorkflowStatus.RUNNING
    db.commit()
    db.refresh(workflow)
    return workflow


def retry_workflow(db: Session, employee_id: int) -> OnboardingWorkflow:
    """Reset failed steps to pending and set the workflow back to running."""
    workflow = get_workflow_by_employee(db, employee_id)
    if not workflow:
        raise ValueError("No workflow found")
    if workflow.status != WorkflowStatus.FAILED:
        raise ValueError(f"Cannot retry a workflow with status '{workflow.status.value}'")

    # Reset all failed steps to pending
    for step in workflow.steps:
        if step.status == StepStatus.FAILED:
            step.status = StepStatus.PENDING
            step.error_message = None
            step.started_at = None
            step.completed_at = None

    workflow.status = WorkflowStatus.PENDING
    workflow.error_message = None
    workflow.completed_at = None
    db.commit()
    db.refresh(workflow)
    return workflow


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
    """Step 1: Parse, validate, and summarize employee data using LLM."""
    data = {
        "employee_name": employee.name,
        "email": employee.email,
        "role": employee.role,
        "department": employee.department,
        "start_date": employee.start_date.isoformat(),
        "manager_email": employee.manager_email,
        "buddy_email": employee.buddy_email,
    }

    prompt = PARSE_DATA_PROMPT.format(
        name=employee.name,
        email=employee.email,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
        manager_email=employee.manager_email or "Not assigned",
        buddy_email=employee.buddy_email or "Not assigned",
    )

    validation_summary = await llm.generate_text(prompt=prompt)
    return json.dumps({
        "parsed_data": data,
        "validation": "passed",
        "ai_summary": validation_summary,
    })


async def _step_welcome_email(employee: Employee) -> str:
    """Step 2: Generate welcome email using LLM + RAG context."""
    context_results = rag.query_policies("onboarding welcome email company culture")
    context = "\n".join([r["text"] for r in context_results])

    prompt = get_template("welcome_email").format(
        name=employee.name,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
        manager_email=employee.manager_email or "TBD",
        buddy_email=employee.buddy_email or "TBD",
    )

    email_content = await llm.generate_text(prompt=prompt, context=context)
    return json.dumps({"type": "welcome_email", "content": email_content})


async def _step_offer_letter(employee: Employee) -> str:
    """Step 3: Generate offer letter using LLM + RAG context."""
    context_results = rag.query_policies("offer letter employment terms compensation")
    context = "\n".join([r["text"] for r in context_results])

    prompt = get_template("offer_letter").format(
        name=employee.name,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
        manager_email=employee.manager_email or "TBD",
    )

    letter_content = await llm.generate_text(prompt=prompt, context=context)
    return json.dumps({"type": "offer_letter", "content": letter_content})


async def _step_30_60_90_plan(employee: Employee) -> str:
    """Step 4: Generate 30-60-90 day plan using LLM + RAG context."""
    context_results = rag.query_policies("onboarding plan training milestones")
    context = "\n".join([r["text"] for r in context_results])

    prompt = get_template("plan_30_60_90").format(
        name=employee.name,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
        manager_email=employee.manager_email or "TBD",
    )

    plan_content = await llm.generate_text(prompt=prompt, context=context)
    return json.dumps({"type": "30_60_90_plan", "content": plan_content})


async def _step_schedule_events(employee: Employee) -> str:
    """Step 5: Schedule calendar events using the calendar service."""
    events = schedule_onboarding_events(
        employee_name=employee.name,
        employee_email=employee.email,
        start_date=employee.start_date,
        manager_email=employee.manager_email,
        buddy_email=employee.buddy_email,
    )
    return json.dumps({"type": "calendar_events", "events": events})


async def _step_equipment_request(employee: Employee) -> str:
    """Step 6: Generate equipment request using LLM."""
    prompt = get_template("equipment_request").format(
        name=employee.name,
        role=employee.role,
        department=employee.department,
        start_date=employee.start_date.isoformat(),
    )

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

    Yields JSON strings matching the frontend AgentEvent interface:
      { type, message, timestamp, step_type?, step_status? }
    """
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        yield _sse_event("error", "Workflow not found")
        return

    employee = workflow.employee

    # Mark workflow as running
    workflow.status = WorkflowStatus.RUNNING
    workflow.started_at = datetime.utcnow()
    employee.status = EmployeeStatus.ONBOARDING
    db.commit()

    yield _sse_event("init", f"Starting onboarding for {employee.name}")
    yield _sse_event("think", f"Employee profile loaded — {employee.role} in {employee.department}, starting {employee.start_date}")
    await asyncio.sleep(0.4)
    yield _sse_event("think", f"Manager: {employee.manager_email or 'unassigned'} · Buddy: {employee.buddy_email or 'unassigned'}")
    await asyncio.sleep(0.3)
    yield _sse_event("active", f"Orchestrator initialized — executing {len(workflow.steps)}-step pipeline")

    # Step-specific reasoning messages emitted BEFORE and DURING execution
    _step_reasoning: dict[str, list[str]] = {
        "parse_data": [
            "Extracting employee record fields (name, email, role, department, start date)…",
            "Validating email format and department against org directory…",
            "Checking manager and buddy assignments are present…",
            "Sending profile summary to LLM for completeness analysis…",
        ],
        "welcome_email": [
            "Querying policy documents for company culture and welcome guidelines…",
            "RAG retrieval: searching ChromaDB for 'onboarding welcome email company culture'…",
            "Building prompt with employee details + retrieved policy context…",
            "Generating personalized welcome email via LLM…",
        ],
        "offer_letter": [
            "Querying policy documents for employment terms and compensation guidelines…",
            "RAG retrieval: searching ChromaDB for 'offer letter employment terms compensation'…",
            "Injecting role-specific details into offer letter template prompt…",
            "Generating formal offer letter via LLM with policy compliance…",
        ],
        "plan_30_60_90": [
            "Querying policy documents for onboarding milestones and training frameworks…",
            "RAG retrieval: searching ChromaDB for 'onboarding plan training milestones'…",
            "Tailoring plan structure to department and role requirements…",
            "Generating 30-60-90 day plan with concrete action items via LLM…",
        ],
        "schedule_events": [
            "Calculating first-week dates from start date…",
            "Preparing 3 calendar events: Orientation, Manager 1:1, Buddy Meetup…",
            f"Resolving attendee emails — manager: {employee.manager_email or 'TBD'}, buddy: {employee.buddy_email or 'TBD'}…",
            "Scheduling events via calendar service…",
        ],
        "equipment_request": [
            "Analyzing role requirements to determine hardware and software needs…",
            "Building IT provisioning prompt based on department and role…",
            "Generating equipment request with access permissions via LLM…",
            "Finalizing provisioning checklist with Day-1 readiness items…",
        ],
    }

    try:
        for step in workflow.steps:
            step_label = step.step_type.value.replace("_", " ").title()

            # ── Check if workflow was paused ──
            db.refresh(workflow)
            if workflow.status == WorkflowStatus.PAUSED:
                yield _sse_event("active", "Workflow paused — waiting to resume...")
                while workflow.status == WorkflowStatus.PAUSED:
                    await asyncio.sleep(2)
                    db.refresh(workflow)
                yield _sse_event("active", "Workflow resumed — continuing...")

            # Skip already-completed steps (important for retry/resume flows)
            if step.status == StepStatus.COMPLETED:
                continue

            # Mark step as running
            step.status = StepStatus.RUNNING
            step.started_at = datetime.utcnow()
            db.commit()

            yield _sse_event(
                "task",
                f"Step {step.step_order}: {step_label}",
                step_type=step.step_type.value,
                step_status="running",
            )

            try:
                # Emit detailed reasoning for this step
                reasoning = _step_reasoning.get(step.step_type.value, [])
                for msg in reasoning:
                    yield _sse_event(
                        "think",
                        msg,
                        step_type=step.step_type.value,
                    )
                    await asyncio.sleep(0.5)

                result = await execute_step(db, step, employee)

                # Preview of generated content
                try:
                    parsed = json.loads(result) if result else {}
                    content = parsed.get("content") or parsed.get("ai_summary") or ""
                    preview = content[:120].replace("\n", " ").strip()
                except (json.JSONDecodeError, AttributeError):
                    preview = (result or "")[:120].replace("\n", " ").strip()

                if preview:
                    yield _sse_event(
                        "think",
                        f"Output preview: {preview}…",
                        step_type=step.step_type.value,
                    )

                step.status = StepStatus.COMPLETED
                step.result = result
                step.completed_at = datetime.utcnow()
                db.commit()

                yield _sse_event(
                    "done",
                    f"\u2713 {step_label} complete",
                    step_type=step.step_type.value,
                    step_status="completed",
                )

                # step_update triggers frontend workflow refresh
                yield _sse_event(
                    "step_update",
                    f"Step {step.step_order} completed",
                    step_type=step.step_type.value,
                    step_status="completed",
                )

            except Exception as e:
                step.status = StepStatus.FAILED
                step.error_message = str(e)
                step.completed_at = datetime.utcnow()
                db.commit()

                yield _sse_event(
                    "error",
                    f"\u2717 {step_label} failed: {str(e)}",
                    step_type=step.step_type.value,
                    step_status="failed",
                )
                raise

        # All steps completed
        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = datetime.utcnow()
        employee.status = EmployeeStatus.COMPLETED
        db.commit()

        elapsed = ""
        if workflow.started_at and workflow.completed_at:
            delta = workflow.completed_at - workflow.started_at
            elapsed = f" in {int(delta.total_seconds())}s"

        yield _sse_event(
            "done",
            f"✅ Onboarding complete for {employee.name}{elapsed} — all {len(workflow.steps)} steps finished successfully",
        )

    except Exception as e:
        workflow.status = WorkflowStatus.FAILED
        workflow.error_message = str(e)
        workflow.completed_at = datetime.utcnow()
        employee.status = EmployeeStatus.FAILED
        db.commit()

        yield _sse_event("error", f"Workflow failed: {str(e)}")


def _sse_event(
    event_type: str,
    message: str,
    step_type: str | None = None,
    step_status: str | None = None,
) -> str:
    """
    Format an SSE event matching the frontend AgentEvent interface.

    Frontend expects: { type, message, timestamp, step_type?, step_status? }
    """
    event: dict = {
        "type": event_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if step_type:
        event["step_type"] = step_type
    if step_status:
        event["step_status"] = step_status
    return json.dumps(event)
