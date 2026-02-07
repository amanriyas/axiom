#!/usr/bin/env python3
"""
Seed script — Populates the database with realistic fake data for testing.

Usage:
    cd backend
    python -m scripts.seed_data

Creates:
    - 12 employees across 6 departments with varied statuses
    - 5 HR policy PDFs (generated via PyMuPDF) + RAG embeddings
    - Completed/failed onboarding workflows with step results
"""

import os
import sys
import hashlib
from datetime import datetime, date, timedelta

# ---------------------------------------------------------------------------
# Ensure project root is importable
# ---------------------------------------------------------------------------
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from app.database import SessionLocal, engine, Base
from app.models import (
    Employee, EmployeeStatus,
    Policy,
    OnboardingWorkflow, WorkflowStatus,
    OnboardingStep, StepType, StepStatus,
    GeneratedDocument, DocumentStatus,
    ApprovalRequest, ApprovalStatus,
    ChatConversation, ChatMessage,
    ComplianceItem, ComplianceStatus,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. EMPLOYEE DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EMPLOYEES = [
    # ── Pending — ready to demo onboarding ────────────────────────
    dict(
        name="Priya Sharma",
        email="priya.sharma@axiom.io",
        role="Senior Frontend Engineer",
        department="Engineering",
        start_date=date(2026, 2, 17),
        manager_email="alex.chen@axiom.io",
        buddy_email="marcus.johnson@axiom.io",
        jurisdiction="US",
        status=EmployeeStatus.PENDING,
    ),
    dict(
        name="James O'Brien",
        email="james.obrien@axiom.io",
        role="Product Designer",
        department="Design",
        start_date=date(2026, 2, 24),
        manager_email="sarah.kim@axiom.io",
        buddy_email="nina.patel@axiom.io",
        jurisdiction="UK",
        status=EmployeeStatus.PENDING,
    ),
    dict(
        name="Amara Okafor",
        email="amara.okafor@axiom.io",
        role="Data Scientist",
        department="Data & Analytics",
        start_date=date(2026, 3, 2),
        manager_email="david.lee@axiom.io",
        buddy_email="carlos.rivera@axiom.io",
        jurisdiction="AE",
        status=EmployeeStatus.PENDING,
    ),
    dict(
        name="Lucas Fernandez",
        email="lucas.fernandez@axiom.io",
        role="DevOps Engineer",
        department="Engineering",
        start_date=date(2026, 3, 2),
        manager_email="alex.chen@axiom.io",
        buddy_email="wei.zhang@axiom.io",
        jurisdiction="DE",
        status=EmployeeStatus.PENDING,
    ),
    dict(
        name="Sophie Williams",
        email="sophie.williams@axiom.io",
        role="Marketing Manager",
        department="Marketing",
        start_date=date(2026, 2, 17),
        manager_email="rachel.green@axiom.io",
        buddy_email="tom.harris@axiom.io",
        jurisdiction="US",
        status=EmployeeStatus.PENDING,
    ),
    dict(
        name="Raj Mehta",
        email="raj.mehta@axiom.io",
        role="Sales Engineer",
        department="Sales",
        start_date=date(2026, 3, 9),
        manager_email="rachel.green@axiom.io",
        buddy_email="sophie.williams@axiom.io",
        jurisdiction="SG",
        status=EmployeeStatus.PENDING,
    ),
    dict(
        name="Olivia Chen",
        email="olivia.chen@axiom.io",
        role="HR Business Partner",
        department="Human Resources",
        start_date=date(2026, 3, 16),
        manager_email="rachel.green@axiom.io",
        buddy_email=None,
        jurisdiction="UK",
        status=EmployeeStatus.PENDING,
    ),

    # ── Completed — already onboarded (shows dashboard history) ──
    dict(
        name="Marcus Johnson",
        email="marcus.johnson@axiom.io",
        role="Backend Engineer",
        department="Engineering",
        start_date=date(2026, 1, 6),
        manager_email="alex.chen@axiom.io",
        buddy_email="wei.zhang@axiom.io",
        jurisdiction="US",
        status=EmployeeStatus.COMPLETED,
    ),
    dict(
        name="Nina Patel",
        email="nina.patel@axiom.io",
        role="UX Researcher",
        department="Design",
        start_date=date(2026, 1, 13),
        manager_email="sarah.kim@axiom.io",
        buddy_email="james.obrien@axiom.io",
        jurisdiction="UK",
        status=EmployeeStatus.COMPLETED,
    ),
    dict(
        name="Carlos Rivera",
        email="carlos.rivera@axiom.io",
        role="ML Engineer",
        department="Data & Analytics",
        start_date=date(2026, 1, 20),
        manager_email="david.lee@axiom.io",
        buddy_email="amara.okafor@axiom.io",
        jurisdiction="AE",
        status=EmployeeStatus.COMPLETED,
    ),

    # ── In-progress ───────────────────────────────────────────────
    dict(
        name="Wei Zhang",
        email="wei.zhang@axiom.io",
        role="Platform Engineer",
        department="Engineering",
        start_date=date(2026, 2, 3),
        manager_email="alex.chen@axiom.io",
        buddy_email="marcus.johnson@axiom.io",
        jurisdiction="US",
        status=EmployeeStatus.ONBOARDING,
    ),

    # ── Failed ────────────────────────────────────────────────────
    dict(
        name="Emily Nakamura",
        email="emily.nakamura@axiom.io",
        role="QA Lead",
        department="Engineering",
        start_date=date(2026, 1, 27),
        manager_email="alex.chen@axiom.io",
        buddy_email="marcus.johnson@axiom.io",
        jurisdiction="US",
        status=EmployeeStatus.FAILED,
    ),
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. POLICY DOCUMENT CONTENT (will be rendered as PDFs)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POLICIES = [
    dict(
        title="Employee Onboarding Guide",
        filename="employee_onboarding_guide.pdf",
        content="""AXIOM INC. — EMPLOYEE ONBOARDING GUIDE

1. WELCOME & ORIENTATION
All new employees will attend a mandatory orientation session on their first day.
The session covers company history, mission, values, and organizational structure.
Orientation runs from 9:00 AM to 12:00 PM and includes a campus tour.

2. FIRST WEEK CHECKLIST
Day 1: Orientation, IT setup, meet your manager and buddy.
Day 2: Department deep-dive, tool access setup, security training.
Day 3: Project overview with team lead, 1:1 with manager.
Day 4: Self-paced training modules (Axiom Academy).
Day 5: Buddy lunch, first week retrospective with manager.

3. EQUIPMENT PROVISIONING
All employees receive a company laptop (MacBook Pro or ThinkPad based on role),
external monitor, ergonomic keyboard/mouse, and noise-canceling headset.
Engineering roles additionally receive cloud development credits and IDE licenses.

4. BUDDY PROGRAM
Every new hire is assigned a buddy from their department who has been with the
company for at least 6 months. Buddies meet with new hires at least twice in
the first month and are available for questions during the first 90 days.

5. 30-60-90 DAY MILESTONES
30 days: Complete training, attend all team ceremonies, first deliverable.
60 days: Independent project ownership, cross-team collaboration.
90 days: Performance review with manager, goal setting for next quarter.

6. FEEDBACK & SUPPORT
New hires receive pulse surveys at 2 weeks, 1 month, and 3 months.
HR Business Partners are available for confidential support at any time.""",
    ),
    dict(
        title="Remote Work & Hybrid Policy",
        filename="remote_work_policy.pdf",
        content="""AXIOM INC. — REMOTE WORK & HYBRID POLICY
Effective Date: January 1, 2026

1. WORK ARRANGEMENT OPTIONS
Axiom supports three work arrangements:
a) In-Office: 5 days per week at company headquarters.
b) Hybrid: 3 days in-office (Tuesday, Wednesday, Thursday) plus 2 days remote.
c) Fully Remote: Available for qualifying roles with VP approval.

2. CORE HOURS
All employees must be available during core hours: 10:00 AM to 3:00 PM
in their local timezone for meetings and real-time collaboration.

3. HOME OFFICE STIPEND
Remote and hybrid employees receive a one-time $1,500 home office setup stipend
and a $100 per month internet and utilities allowance.

4. COMMUNICATION EXPECTATIONS
Respond to Slack messages within 2 hours during core hours.
Camera on for team meetings and client calls.
Update Slack status when stepping away for more than 30 minutes.
Weekly async status updates in team channels every Friday.

5. IN-OFFICE REQUIREMENTS FOR HYBRID
Hybrid employees must be in-office on Tuesday, Wednesday, and Thursday.
Teams may designate additional in-office days for sprint planning or launches.
Hot-desking is available; reserved desks require manager approval.

6. EQUIPMENT FOR REMOTE WORKERS
Remote employees receive the same equipment as in-office employees.
IT ships equipment to the employee's registered home address.
All company equipment must be returned within 14 days of separation.""",
    ),
    dict(
        title="Code of Conduct & Ethics",
        filename="code_of_conduct.pdf",
        content="""AXIOM INC. — CODE OF CONDUCT & ETHICS

1. OUR VALUES
Axiom is built on four core values: Innovation, Integrity, Inclusion, and Impact.
Every employee is expected to embody these values in their daily work.

2. PROFESSIONAL CONDUCT
Treat all colleagues, clients, and partners with respect and dignity.
Maintain a harassment-free workplace (zero tolerance policy).
Protect confidential information and intellectual property.
Avoid conflicts of interest and disclose potential conflicts to your manager.
Follow all applicable laws and regulations.

3. DIVERSITY, EQUITY & INCLUSION
Axiom is committed to building a diverse team. We do not discriminate based on
race, color, religion, gender, sexual orientation, national origin, age, disability,
or any other protected characteristic. Our ERGs are open to all employees.

4. DATA PRIVACY & SECURITY
Never share passwords or access credentials.
Use company-approved tools for all work communications.
Report suspected security incidents to security@axiom.io immediately.
Complete annual security awareness training (mandatory).
Follow the principle of least privilege for data access.

5. SOCIAL MEDIA
Employees may use social media but must clearly state that views are their own.
Do not share proprietary information or unreleased product details on public platforms.

6. REPORTING CONCERNS
Use the anonymous ethics hotline (ethics@axiom.io) or speak to your HR Business
Partner to report any concerns. Axiom has a strict no-retaliation policy.""",
    ),
    dict(
        title="Benefits & Compensation Overview",
        filename="benefits_compensation.pdf",
        content="""AXIOM INC. — BENEFITS & COMPENSATION OVERVIEW

1. COMPENSATION PHILOSOPHY
Axiom targets the 75th percentile of market compensation for all roles.
Salary bands are reviewed annually. All offers include base salary, equity, and bonus.

2. HEALTH BENEFITS (effective Day 1)
Medical: Choice of PPO or HDHP with HSA (company contributes $1,500 per year to HSA).
Dental: Delta Dental PPO, covers orthodontia up to $2,000 lifetime.
Vision: VSP, $200 annual frame allowance.
Mental Health: Free access to Calm app plus 12 free therapy sessions per year via Lyra.

3. EQUITY
All full-time employees receive stock options vesting over 4 years with a 1-year cliff.
Refresh grants are awarded annually based on performance and market adjustments.

4. PAID TIME OFF
Unlimited PTO with a minimum of 15 days encouraged.
12 company holidays per year.
2 floating holidays (use anytime).
Sick leave: unlimited (honor system).
Parental leave: 16 weeks fully paid for both birth and non-birth parents.

5. RETIREMENT
401(k) with 4% company match and immediate vesting.
Access to financial advisor for quarterly sessions.

6. PROFESSIONAL DEVELOPMENT
$3,000 per year learning and development budget.
Conference attendance: 1 per year, company-funded.
Internal mentorship program.
Axiom Academy: 200+ self-paced courses.

7. OTHER PERKS
Commuter benefits (pre-tax transit and parking).
Gym membership reimbursement ($75 per month).
Employee referral bonus: $5,000 per successful hire.
Free lunch on in-office days (Tuesday through Thursday).""",
    ),
    dict(
        title="Information Security Policy",
        filename="information_security_policy.pdf",
        content="""AXIOM INC. — INFORMATION SECURITY POLICY

1. PURPOSE
This policy establishes security requirements for all Axiom employees,
contractors, and third parties who access Axiom systems and data.

2. CLASSIFICATION OF DATA
Public: Marketing materials, blog posts, open-source code.
Internal: Slack messages, internal docs, meeting notes.
Confidential: Customer data, financials, employee PII, source code.
Restricted: Encryption keys, access credentials, security audit reports.

3. ACCESS CONTROL
All systems require multi-factor authentication (MFA).
Access follows the principle of least privilege.
Manager approval required for production system access.
Quarterly access reviews conducted by the Security team.
Immediate access revocation upon employee separation.

4. DEVICE SECURITY
Company devices must have full-disk encryption enabled.
Screen lock required after 5 minutes of inactivity.
Personal devices may access email only via the approved MDM solution.
No company data on personal USB drives or cloud storage accounts.

5. INCIDENT RESPONSE
If you suspect a security incident:
a) Do NOT attempt to fix it yourself.
b) Report immediately to security@axiom.io or the Slack channel.
c) Preserve evidence such as screenshots and logs.
d) The Security team will respond within 1 hour during business hours.

6. ACCEPTABLE USE
Company systems are for business use; limited personal use is acceptable.
No torrenting, illegal downloads, or unapproved software installation.
VPN required when connecting from public networks.
Annual security awareness training is mandatory (due by March 31 each year).

7. COMPLIANCE
Axiom complies with SOC 2 Type II, GDPR, and CCPA requirements.
All employees handling customer data must complete privacy training annually.""",
    ),
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. COMPLETED WORKFLOW STEP RESULTS (realistic AI-generated content)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _step_results(emp_name, emp_role, emp_dept, emp_start, mgr, buddy, jurisdiction="US"):
    """Return a dict of step_type -> realistic result text for a completed workflow."""
    jurisdiction_labels = {
        "US": "United States", "UK": "United Kingdom", "AE": "United Arab Emirates",
        "DE": "Germany", "SG": "Singapore",
    }
    jur_label = jurisdiction_labels.get(jurisdiction, jurisdiction)

    return {
        StepType.PARSE_DATA: f"""# Employee Data Validation — {emp_name}

**Status:** All fields validated successfully

| Field | Value | Status |
|-------|-------|--------|
| Name | {emp_name} | Valid |
| Role | {emp_role} | Valid |
| Department | {emp_dept} | Matches org chart |
| Start Date | {emp_start} | Valid (weekday) |
| Manager | {mgr} | Found in directory |
| Buddy | {buddy} | Found in directory |
| Jurisdiction | {jurisdiction} | {jur_label} |

**Assessment:** All critical fields present and validated. Ready to proceed with onboarding.""",

        StepType.DETECT_JURISDICTION: f"""# Jurisdiction Detection — {emp_name}

**Detected Jurisdiction:** {jurisdiction} ({jur_label})

**Detection Method:** Employee profile field
**Confidence:** 100% (explicitly set)

**Applicable Legal Frameworks:**
- Employment law: {jur_label} labor regulations
- Tax withholding: {jurisdiction} tax authority rules
- Benefits: {jurisdiction}-compliant benefits package
- Data protection: {"GDPR" if jurisdiction in ("UK", "DE") else "Local regulations"}

**Document Templates:** Loading {jurisdiction}-specific templates for employment contract, NDA, and equity agreement.

**Status:** Jurisdiction confirmed. Proceeding with {jurisdiction}-specific document generation.""",

        StepType.EMPLOYMENT_CONTRACT: f"""# Employment Contract — {emp_name}

**Jurisdiction:** {jurisdiction} ({jur_label})
**Document Status:** Generated successfully

---

EMPLOYMENT AGREEMENT ({jur_label.upper()})

This Employment Agreement is entered into as of {emp_start}, by and between Axiom Inc. and {emp_name}.

**1. POSITION:** {emp_role}, {emp_dept} department. Reports to {mgr.split('@')[0].replace('.', ' ').title()}.

**2. EMPLOYMENT TYPE:** Full-time, {"at-will" if jurisdiction == "US" else "permanent contract"}.

**3. COMPENSATION:** As detailed in the attached compensation schedule.

**4. BENEFITS:** Employee is entitled to all benefits per {jurisdiction} employment law.

**5. TERMINATION:** {"Either party may terminate at any time (at-will)." if jurisdiction == "US" else f"Subject to {jur_label} labor law notice periods."}

**6. GOVERNING LAW:** This agreement is governed by the laws of {jur_label}.

Signed: ________________________     Date: ________""",

        StepType.NDA: f"""# Non-Disclosure Agreement — {emp_name}

**Jurisdiction:** {jurisdiction} ({jur_label})
**Document Status:** Generated successfully

---

NON-DISCLOSURE AGREEMENT

Between Axiom Inc. ("Company") and {emp_name} ("Employee"), effective {emp_start}.

**1. CONFIDENTIAL INFORMATION:** All non-public business information, source code, customer data, and trade secrets.

**2. OBLIGATIONS:** Employee shall maintain strict confidentiality, use information only for employment purposes, and return all materials upon separation.

**3. DURATION:** {"2 years post-employment" if jurisdiction == "US" else "Indefinite for trade secrets, 1 year for other confidential information"}.

**4. REMEDIES:** Company is entitled to injunctive relief and damages for breach.

**5. GOVERNING LAW:** {jur_label} | {"Arbitration in employee's home state" if jurisdiction == "US" else f"Jurisdiction of {jur_label} courts"}.""",

        StepType.EQUITY_AGREEMENT: f"""# Equity Agreement — {emp_name}

**Jurisdiction:** {jurisdiction} ({jur_label})
**Document Status:** Generated successfully

---

STOCK OPTION GRANT AGREEMENT

Axiom Inc. grants to {emp_name} stock options under the Company's Equity Incentive Plan.

**Grant Details:**
- Vesting Schedule: 4-year vest, 1-year cliff
- Exercise Period: 10 years from grant date
- Option Type: {"ISO (Incentive Stock Options)" if jurisdiction == "US" else "Non-qualified options"}

**Tax Treatment:**
{"- Subject to IRC Section 422 (ISO rules)" if jurisdiction == "US" else f"- Subject to {jur_label} tax regulations on equity compensation"}
{"- AMT considerations apply at exercise" if jurisdiction == "US" else ""}

**Termination:** Unvested options forfeit upon separation. Vested options exercisable for 90 days post-separation.""",

        StepType.OFFER_LETTER: f"""# OFFER OF EMPLOYMENT — CONFIDENTIAL

Date: {(datetime.strptime(str(emp_start), '%Y-%m-%d') - timedelta(days=14)).strftime('%B %d, %Y')}

Dear {emp_name},

We are pleased to extend an offer of employment for the position of **{emp_role}** in the **{emp_dept}** department at Axiom Inc.

**Position Details:**
- Title: {emp_role}
- Department: {emp_dept}
- Start Date: {emp_start}
- Reports To: {mgr.split('@')[0].replace('.', ' ').title()}
- Location: {"Hybrid (3 days in-office)" if jurisdiction == "US" else f"{jur_label} office — hybrid"}
- Employment Type: Full-time, {"Exempt" if jurisdiction == "US" else "Permanent"}
- Jurisdiction: {jurisdiction} ({jur_label})

**Benefits (effective Day 1):**
- Medical, Dental, Vision insurance
- {"401(k) with 4% match" if jurisdiction == "US" else "Pension scheme per local requirements"}
- {"Unlimited PTO (minimum 15 days encouraged)" if jurisdiction == "US" else f"Annual leave per {jur_label} statutory minimum + 5 additional days"}
- $3,000/year learning and development budget

This offer is contingent upon successful background verification.

Sincerely,
Rachel Green, VP of People Operations""",

        StepType.WELCOME_EMAIL: f"""**Subject: Welcome to Axiom, {emp_name.split()[0]}!**

Dear {emp_name.split()[0]},

We are thrilled to welcome you to the {emp_dept} team at Axiom as our new {emp_role}! Your first day is {emp_start}, and we have put together an exciting schedule for you.

**Your First Day:**
- 9:00 AM — Orientation session (Building A, Room 201)
- 11:00 AM — Meet your manager {mgr.split('@')[0].replace('.', ' ').title()} and buddy {buddy.split('@')[0].replace('.', ' ').title() if buddy else 'TBD'}
- 12:00 PM — Welcome lunch with the {emp_dept} team
- 1:00 PM — IT setup and equipment collection

**Before You Arrive:**
- Check your personal email for IT setup instructions
- Bring a valid photo ID for your access badge
- Parking pass will be at the front desk

We can not wait to have you on the team.

Best regards,
The Axiom People Team""",

        StepType.PLAN_30_60_90: f"""# 30-60-90 Day Plan — {emp_name}, {emp_role}

## First 30 Days — Learn and Orient
- Complete Axiom Academy onboarding modules
- Set up development environment and tools
- Review {emp_dept} team documentation and processes
- Shadow senior team members on active projects
- Attend all team ceremonies (standup, sprint planning, retro)
- Weekly 1:1 with manager every Friday at 2:00 PM

## Days 31-60 — Contribute and Build
- Ship first production deliverable
- Take ownership of one project area
- Participate in cross-team collaboration
- Complete security training and get production access
- Mid-point feedback session with manager

## Days 61-90 — Own and Lead
- Own and deliver a project end-to-end
- Lead one team meeting or planning session
- Write documentation for your area of ownership
- Present work to the broader {emp_dept} team
- 90-day performance review with manager
- Set OKRs for next quarter""",

        StepType.SCHEDULE_EVENTS: f"""Calendar Events Scheduled for {emp_name}:

1. Orientation Session — {emp_start}, 9:00 AM - 12:00 PM (Building A, Room 201)
2. Manager 1:1 with {mgr.split('@')[0].replace('.', ' ').title()} — {emp_start}, 3:00 PM
3. Buddy Meetup with {buddy.split('@')[0].replace('.', ' ').title() if buddy else 'TBD'} — Day 2, 12:00 PM
4. IT Setup — {emp_start}, 1:00 PM - 2:00 PM (IT Help Desk)
5. 30-Day Check-in — 30 days after start, 2:00 PM""",

        StepType.EQUIPMENT_REQUEST: f"""# IT Equipment Request — {emp_name}

**Role:** {emp_role} | **Department:** {emp_dept} | **Start Date:** {emp_start}

## Hardware
- MacBook Pro 16" M3 Pro (32GB RAM, 1TB SSD)
- Dell U2723QE 27" 4K Monitor
- Logitech MX Keys keyboard + MX Master 3S mouse
- Jabra Evolve2 75 headset
- Employee access badge

## Software Licenses
- GitHub Enterprise access
- Slack workspace (added to #{emp_dept.lower().replace(' & ', '-').replace(' ', '-')}, #new-hires)
- Jira project access ({emp_dept} board)
- Confluence {emp_dept} space
- 1Password Teams vault

## Cloud & Access
- SSO access provisioned
- VPN credentials
- Email account: {emp_name.split()[0].lower()}.{emp_name.split()[-1].lower()}@axiom.io

**Provisioning Status:** All items ready for pickup at IT desk on {emp_start}""",
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PDF Generation via PyMuPDF (fitz)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_pdf_bytes(text: str) -> bytes:
    """Generate a valid PDF from plain text using PyMuPDF (fitz)."""
    import fitz  # PyMuPDF

    doc = fitz.open()  # new empty PDF
    lines = text.strip().split("\n")

    # Page dimensions
    page_width, page_height = 612, 792  # US Letter
    margin_x, margin_top, margin_bottom = 54, 54, 54
    usable_width = page_width - 2 * margin_x
    y = margin_top

    page = doc.new_page(width=page_width, height=page_height)

    for line in lines:
        # Determine font size / style
        stripped = line.strip()
        if not stripped:
            y += 10
            if y > page_height - margin_bottom:
                page = doc.new_page(width=page_width, height=page_height)
                y = margin_top
            continue

        if stripped.startswith("AXIOM") or (stripped == stripped.upper() and len(stripped) > 10):
            fontsize = 12
            fontname = "helv"
        elif stripped[0].isdigit() and "." in stripped[:3]:
            fontsize = 11
            fontname = "helv"
        else:
            fontsize = 9.5
            fontname = "helv"

        line_height = fontsize + 5

        # Check page overflow
        if y + line_height > page_height - margin_bottom:
            page = doc.new_page(width=page_width, height=page_height)
            y = margin_top

        # Insert text
        page.insert_text(
            fitz.Point(margin_x, y),
            stripped,
            fontsize=fontsize,
            fontname=fontname,
        )
        y += line_height

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SEED FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def seed_employees(db):
    """Insert fake employees, skip duplicates by email."""
    now = datetime.utcnow()
    created = 0

    for i, emp in enumerate(EMPLOYEES):
        if db.query(Employee).filter(Employee.email == emp["email"]).first():
            print(f"  ⏭️  Skip (exists): {emp['name']}")
            continue

        # Realistic timestamps per status
        if emp["status"] == EmployeeStatus.COMPLETED:
            created_at = now - timedelta(days=35 + i * 5)
            updated_at = created_at + timedelta(days=3)
        elif emp["status"] == EmployeeStatus.ONBOARDING:
            created_at = now - timedelta(days=5)
            updated_at = now - timedelta(hours=2)
        elif emp["status"] == EmployeeStatus.FAILED:
            created_at = now - timedelta(days=12)
            updated_at = now - timedelta(days=10)
        else:
            created_at = now - timedelta(days=i)
            updated_at = created_at

        employee = Employee(
            name=emp["name"],
            email=emp["email"],
            role=emp["role"],
            department=emp["department"],
            start_date=emp["start_date"],
            manager_email=emp.get("manager_email"),
            buddy_email=emp.get("buddy_email"),
            jurisdiction=emp.get("jurisdiction", "US"),
            status=emp["status"],
            created_at=created_at,
            updated_at=updated_at,
        )
        db.add(employee)
        created += 1
        status_icon = {
            EmployeeStatus.PENDING: "🟡",
            EmployeeStatus.ONBOARDING: "🔵",
            EmployeeStatus.COMPLETED: "🟢",
            EmployeeStatus.FAILED: "🔴",
        }.get(emp["status"], "⚪")
        print(f"  ✅ {status_icon} {emp['name']} — {emp['role']} ({emp['status'].value})")

    db.commit()
    return created


def seed_policies(db):
    """Generate PDFs, save to disk/DB, and embed into ChromaDB."""
    from app.services.rag import embed_policy

    policy_dir = os.path.join(BACKEND_DIR, "data", "policies")
    os.makedirs(policy_dir, exist_ok=True)

    created = 0
    for pol in POLICIES:
        if db.query(Policy).filter(Policy.title == pol["title"]).first():
            print(f"  ⏭️  Skip (exists): {pol['title']}")
            continue

        # Generate a real PDF
        pdf_bytes = generate_pdf_bytes(pol["content"])
        content_hash = hashlib.sha256(pdf_bytes).hexdigest()
        file_path = os.path.join(policy_dir, pol["filename"])

        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        policy = Policy(
            title=pol["title"],
            filename=pol["filename"],
            file_path=file_path,
            content_hash=content_hash,
            file_size=len(pdf_bytes),
            is_embedded=False,
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)

        # Embed into vector store
        try:
            num_chunks = embed_policy(policy.id, file_path, pol["title"])
            policy.is_embedded = True
            db.commit()
            print(f"  ✅ {pol['title']} — {len(pdf_bytes):,} bytes, {num_chunks} chunks embedded")
        except Exception as e:
            print(f"  ⚠️  {pol['title']} — saved but embedding failed: {e}")

        created += 1

    return created


def seed_workflows(db):
    """Create completed/failed workflows with step results."""
    STEP_ORDER = [
        StepType.PARSE_DATA,
        StepType.DETECT_JURISDICTION,
        StepType.EMPLOYMENT_CONTRACT,
        StepType.NDA,
        StepType.EQUITY_AGREEMENT,
        StepType.OFFER_LETTER,
        StepType.WELCOME_EMAIL,
        StepType.PLAN_30_60_90,
        StepType.SCHEDULE_EVENTS,
        StepType.EQUIPMENT_REQUEST,
    ]

    created = 0

    # ── Completed workflows ──────────────────────────────────────
    completed_emps = db.query(Employee).filter(
        Employee.status == EmployeeStatus.COMPLETED
    ).all()

    for employee in completed_emps:
        if db.query(OnboardingWorkflow).filter(
            OnboardingWorkflow.employee_id == employee.id
        ).first():
            print(f"  ⏭️  Skip (exists): Workflow for {employee.name}")
            continue

        started_at = employee.created_at + timedelta(hours=1)
        completed_at = employee.updated_at

        workflow = OnboardingWorkflow(
            employee_id=employee.id,
            status=WorkflowStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            created_at=employee.created_at,
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        results = _step_results(
            employee.name, employee.role, employee.department,
            str(employee.start_date),
            employee.manager_email or "manager@axiom.io",
            employee.buddy_email or "",
            jurisdiction=employee.jurisdiction or "US",
        )

        # Steps that require approval (document generation steps)
        approval_steps = {StepType.EMPLOYMENT_CONTRACT, StepType.NDA, StepType.EQUITY_AGREEMENT, StepType.OFFER_LETTER}

        for i, step_type in enumerate(STEP_ORDER):
            step_started = started_at + timedelta(minutes=i * 2)
            step_completed = step_started + timedelta(minutes=1, seconds=30)
            step = OnboardingStep(
                workflow_id=workflow.id,
                step_type=step_type,
                step_order=i + 1,
                status=StepStatus.COMPLETED,
                result=results.get(step_type, "Completed successfully."),
                requires_approval=step_type in approval_steps,
                approval_status="approved" if step_type in approval_steps else None,
                started_at=step_started,
                completed_at=step_completed,
            )
            db.add(step)

        db.commit()
        created += 1
        print(f"  ✅ 🟢 Completed workflow: {employee.name} (10/10 steps)")

    # ── Failed workflows ─────────────────────────────────────────
    failed_emps = db.query(Employee).filter(
        Employee.status == EmployeeStatus.FAILED
    ).all()

    for employee in failed_emps:
        if db.query(OnboardingWorkflow).filter(
            OnboardingWorkflow.employee_id == employee.id
        ).first():
            print(f"  ⏭️  Skip (exists): Workflow for {employee.name}")
            continue

        started_at = employee.created_at + timedelta(hours=1)

        workflow = OnboardingWorkflow(
            employee_id=employee.id,
            status=WorkflowStatus.FAILED,
            started_at=started_at,
            completed_at=employee.updated_at,
            error_message="LLM API rate limit exceeded during offer letter generation",
            created_at=employee.created_at,
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        results = _step_results(
            employee.name, employee.role, employee.department,
            str(employee.start_date),
            employee.manager_email or "manager@axiom.io",
            employee.buddy_email or "",
            jurisdiction=employee.jurisdiction or "US",
        )

        # Failed at step 4 (employment_contract — index 2 in new 10-step pipeline)
        for i, step_type in enumerate(STEP_ORDER):
            if i < 2:
                status = StepStatus.COMPLETED
                result = results.get(step_type, "Done.")
                s_started = started_at + timedelta(minutes=i * 2)
                s_completed = s_started + timedelta(minutes=1)
                error = None
            elif i == 2:
                status = StepStatus.FAILED
                result = None
                s_started = started_at + timedelta(minutes=i * 2)
                s_completed = s_started + timedelta(seconds=30)
                error = "LLM API rate limit exceeded"
            else:
                status = StepStatus.PENDING
                result = None
                s_started = None
                s_completed = None
                error = None

            step = OnboardingStep(
                workflow_id=workflow.id,
                step_type=step_type,
                step_order=i + 1,
                status=status,
                result=result,
                error_message=error,
                started_at=s_started,
                completed_at=s_completed,
            )
            db.add(step)

        db.commit()
        created += 1
        print(f"  ✅ 🔴 Failed workflow: {employee.name} (failed at step 3: employment_contract)")

    # ── In-progress workflow (partial) ───────────────────────────
    onboarding_emps = db.query(Employee).filter(
        Employee.status == EmployeeStatus.ONBOARDING
    ).all()

    for employee in onboarding_emps:
        if db.query(OnboardingWorkflow).filter(
            OnboardingWorkflow.employee_id == employee.id
        ).first():
            print(f"  ⏭️  Skip (exists): Workflow for {employee.name}")
            continue

        started_at = employee.created_at + timedelta(hours=1)

        workflow = OnboardingWorkflow(
            employee_id=employee.id,
            status=WorkflowStatus.RUNNING,
            started_at=started_at,
            created_at=employee.created_at,
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        results = _step_results(
            employee.name, employee.role, employee.department,
            str(employee.start_date),
            employee.manager_email or "manager@axiom.io",
            employee.buddy_email or "",
            jurisdiction=employee.jurisdiction or "US",
        )

        # First 4 steps completed, 5th running (equity_agreement)
        for i, step_type in enumerate(STEP_ORDER):
            if i < 4:
                # First 4 steps completed (parse_data, detect_jurisdiction, employment_contract, nda)
                status = StepStatus.COMPLETED
                result = results.get(step_type, "Done.")
                s_started = started_at + timedelta(minutes=i * 2)
                s_completed = s_started + timedelta(minutes=1, seconds=30)
            elif i == 4:
                # 5th step is running (equity_agreement)
                status = StepStatus.RUNNING
                result = None
                s_started = started_at + timedelta(minutes=i * 2)
                s_completed = None
            else:
                # Remaining are pending
                status = StepStatus.PENDING
                result = None
                s_started = None
                s_completed = None

            step = OnboardingStep(
                workflow_id=workflow.id,
                step_type=step_type,
                step_order=i + 1,
                status=status,
                result=result,
                started_at=s_started,
                completed_at=s_completed,
            )
            db.add(step)

        db.commit()
        created += 1
        print(f"  ✅ 🔵 In-progress workflow: {employee.name} (4/10 steps done, step 5 running)")

    return created


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SEED: Generated Documents + Approval Requests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def seed_documents_and_approvals(db):
    """Create generated documents and approval requests for completed employees
    so the Approvals page has data to show immediately."""
    if db.query(GeneratedDocument).first():
        print("  ⏭️  Skip (documents already exist)")
        return 0

    completed_emps = db.query(Employee).filter(
        Employee.status == EmployeeStatus.COMPLETED
    ).all()

    if not completed_emps:
        print("  ⏭️  No completed employees found")
        return 0

    doc_types = ["employment_contract", "nda", "equity_agreement", "offer_letter"]
    now = datetime.utcnow()
    doc_count = 0
    approval_count = 0

    for emp in completed_emps:
        jurisdiction = emp.jurisdiction or "US"

        for dtype in doc_types:
            doc = GeneratedDocument(
                employee_id=emp.id,
                document_type=dtype,
                jurisdiction=jurisdiction,
                content=f"# {dtype.replace('_', ' ').title()} — {emp.name}\n\n"
                         f"**Jurisdiction:** {jurisdiction}\n"
                         f"**Employee:** {emp.name}\n"
                         f"**Role:** {emp.role}\n"
                         f"**Department:** {emp.department}\n"
                         f"**Start Date:** {emp.start_date}\n\n"
                         f"This is a generated {dtype.replace('_', ' ')} document.\n"
                         f"Full content would be generated by the AI pipeline.",
                status=DocumentStatus.APPROVED,
                version=1,
                generated_at=now - timedelta(days=30),
                approved_at=now - timedelta(days=28),
            )
            db.add(doc)
            db.flush()  # get doc.id

            # Create approval request — approved for completed employees
            approval = ApprovalRequest(
                employee_id=emp.id,
                document_id=doc.id,
                status=ApprovalStatus.APPROVED,
                comments=f"Reviewed and approved — {dtype.replace('_', ' ')} for {emp.name}",
                created_at=now - timedelta(days=30),
                reviewed_at=now - timedelta(days=28),
            )
            db.add(approval)
            doc_count += 1
            approval_count += 1

        print(f"  ✅ {emp.name} — 4 documents + 4 approvals (approved)")

    # Add some pending approvals for the in-progress / pending employees to give the UI something to review
    pending_emps = db.query(Employee).filter(
        Employee.status.in_([EmployeeStatus.PENDING, EmployeeStatus.ONBOARDING])
    ).limit(3).all()

    for emp in pending_emps:
        jurisdiction = emp.jurisdiction or "US"
        # Create 2-3 pending documents for each
        for dtype in doc_types[:3]:  # employment_contract, nda, equity_agreement
            doc = GeneratedDocument(
                employee_id=emp.id,
                document_type=dtype,
                jurisdiction=jurisdiction,
                content=f"# {dtype.replace('_', ' ').title()} — {emp.name}\n\n"
                         f"**Jurisdiction:** {jurisdiction}\n"
                         f"**Employee:** {emp.name}\n"
                         f"**Role:** {emp.role}\n"
                         f"**Department:** {emp.department}\n"
                         f"**Start Date:** {emp.start_date}\n\n"
                         f"---\n\n"
                         f"## DRAFT — Pending Review\n\n"
                         f"This {dtype.replace('_', ' ')} document has been generated by the AI pipeline "
                         f"and is awaiting human review and approval before the onboarding workflow can continue.\n\n"
                         f"### Key Clauses\n"
                         f"- Employment terms per {jurisdiction} regulations\n"
                         f"- Compensation and benefits package\n"
                         f"- Termination provisions\n"
                         f"- Confidentiality obligations\n",
                status=DocumentStatus.PENDING_APPROVAL,
                version=1,
                generated_at=now - timedelta(hours=6),
            )
            db.add(doc)
            db.flush()

            approval = ApprovalRequest(
                employee_id=emp.id,
                document_id=doc.id,
                status=ApprovalStatus.PENDING,
                created_at=now - timedelta(hours=6),
            )
            db.add(approval)
            doc_count += 1
            approval_count += 1

        print(f"  ✅ {emp.name} — 3 documents + 3 approvals (pending review)")

    db.commit()
    print(f"\n  📊 Total: {doc_count} documents, {approval_count} approvals")
    return doc_count


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SEED: Chat Conversations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def seed_chat_conversations(db):
    """Create sample chat conversations to populate the Chat page."""
    if db.query(ChatConversation).first():
        print("  ⏭️  Skip (conversations already exist)")
        return 0

    now = datetime.utcnow()
    convos = [
        {
            "title": "PTO Policy Questions",
            "started_at": now - timedelta(days=3),
            "messages": [
                ("user", "What is the PTO policy at Axiom?", None),
                ("assistant",
                 "Axiom offers **unlimited PTO** with a minimum of 15 days encouraged per year. "
                 "In addition, there are:\n\n"
                 "- **12 company holidays** per year\n"
                 "- **2 floating holidays** (use anytime)\n"
                 "- **Unlimited sick leave** (honor system)\n"
                 "- **16 weeks parental leave** (fully paid for both birth and non-birth parents)\n\n"
                 "The company encourages employees to take regular time off to maintain work-life balance.",
                 '["Benefits & Compensation Overview"]'),
                ("user", "Is there a minimum number of days I need to take?", None),
                ("assistant",
                 "While PTO is unlimited, Axiom **strongly encourages a minimum of 15 days per year**. "
                 "This is not a cap — it is the recommended floor. The company believes regular time off "
                 "improves productivity and well-being. Managers will check in if they notice team members "
                 "aren't taking enough time off.",
                 '["Benefits & Compensation Overview"]'),
            ],
        },
        {
            "title": "Remote Work Setup",
            "started_at": now - timedelta(days=1),
            "messages": [
                ("user", "What equipment do remote employees get?", None),
                ("assistant",
                 "Remote and hybrid employees receive the **same equipment as in-office employees**:\n\n"
                 "- Company laptop (MacBook Pro or ThinkPad based on role)\n"
                 "- External monitor\n"
                 "- Ergonomic keyboard/mouse\n"
                 "- Noise-canceling headset\n\n"
                 "Additionally, remote employees get:\n"
                 "- A one-time **$1,500 home office setup stipend**\n"
                 "- A **$100/month** internet and utilities allowance\n\n"
                 "IT will ship all equipment to your registered home address.",
                 '["Remote Work & Hybrid Policy", "Employee Onboarding Guide"]'),
                ("user", "What are the core hours I need to be available?", None),
                ("assistant",
                 "All employees must be available during **core hours: 10:00 AM to 3:00 PM** "
                 "in their local timezone. This is for meetings and real-time collaboration.\n\n"
                 "Outside core hours, you have flexibility in how you structure your workday. "
                 "The key communication expectations are:\n"
                 "- Respond to Slack messages within 2 hours during core hours\n"
                 "- Camera on for team meetings and client calls\n"
                 "- Update Slack status when stepping away for 30+ minutes\n"
                 "- Weekly async status updates every Friday",
                 '["Remote Work & Hybrid Policy"]'),
            ],
        },
        {
            "title": "Security Training Requirements",
            "started_at": now - timedelta(hours=5),
            "messages": [
                ("user", "When is security training due?", None),
                ("assistant",
                 "Annual security awareness training is **mandatory and due by March 31 each year**. "
                 "All employees, contractors, and third parties who access Axiom systems must complete it.\n\n"
                 "The training covers:\n"
                 "- Data classification and handling\n"
                 "- MFA and access control best practices\n"
                 "- Incident response procedures\n"
                 "- Acceptable use policies\n\n"
                 "Axiom complies with **SOC 2 Type II, GDPR, and CCPA** requirements.",
                 '["Information Security Policy"]'),
            ],
        },
    ]

    count = 0
    for conv_data in convos:
        conv = ChatConversation(
            title=conv_data["title"],
            started_at=conv_data["started_at"],
            last_message_at=conv_data["started_at"] + timedelta(minutes=len(conv_data["messages"]) * 2),
        )
        db.add(conv)
        db.flush()

        for idx, (role, content, sources) in enumerate(conv_data["messages"]):
            msg = ChatMessage(
                conversation_id=conv.id,
                role=role,
                content=content,
                sources=sources,
                created_at=conv_data["started_at"] + timedelta(minutes=idx * 2),
            )
            db.add(msg)

        count += 1
        print(f"  ✅ \"{conv_data['title']}\" — {len(conv_data['messages'])} messages")

    db.commit()
    return count


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print()
    print("=" * 62)
    print("  🌱 AXIOM — DATABASE SEED SCRIPT")
    print("=" * 62)

    # Ensure all tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("\n👤 Seeding Employees...")
        emp_count = seed_employees(db)

        print("\n📄 Seeding Policy Documents + RAG Embeddings...")
        pol_count = seed_policies(db)

        print("\n🔄 Seeding Onboarding Workflows...")
        wf_count = seed_workflows(db)

        print("\n📝 Seeding Generated Documents & Approvals...")
        doc_count = seed_documents_and_approvals(db)

        print("\n💬 Seeding Chat Conversations...")
        chat_count = seed_chat_conversations(db)

        # ── Summary ──────────────────────────────────────────────
        print()
        print("=" * 62)
        print("  ✅ SEED COMPLETE")
        print("=" * 62)
        print(f"  New employees:      {emp_count}")
        print(f"  New policies:       {pol_count}")
        print(f"  New workflows:      {wf_count}")
        print(f"  New documents:      {doc_count}")
        print(f"  New conversations:  {chat_count}")

        total_emp = db.query(Employee).count()
        total_pol = db.query(Policy).count()
        total_wf = db.query(OnboardingWorkflow).count()
        total_docs = db.query(GeneratedDocument).count()
        total_approvals = db.query(ApprovalRequest).count()
        total_compliance = db.query(ComplianceItem).count()
        total_chats = db.query(ChatConversation).count()
        pending = db.query(Employee).filter(Employee.status == EmployeeStatus.PENDING).count()
        pending_approvals = db.query(ApprovalRequest).filter(ApprovalRequest.status == ApprovalStatus.PENDING).count()

        print()
        print(f"  📊 DB totals:")
        print(f"     {total_emp} employees, {total_pol} policies, {total_wf} workflows")
        print(f"     {total_docs} documents, {total_approvals} approvals ({pending_approvals} pending)")
        print(f"     {total_compliance} compliance items, {total_chats} chat conversations")
        print(f"  🎯 {pending} employees are PENDING — ready to run onboarding!")
        print("=" * 62)
        print()

    finally:
        db.close()


if __name__ == "__main__":
    main()
