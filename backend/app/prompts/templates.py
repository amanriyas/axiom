# app/prompts/templates.py
"""
Structured prompt templates for the Zero-Touch Onboarding Orchestrator.

Each template uses Python str.format() placeholders for dynamic values.
RAG context is injected separately via the `context` parameter in llm.generate_text().
"""

# ─────────────────────────────────────────────────────────────
# System prompt — shared across all generation steps
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert HR onboarding assistant for a modern technology company.
Your role is to generate professional, warm, and actionable onboarding documents.

Guidelines:
- Be specific and personalized — use the employee's name, role, and department throughout
- Use a professional but friendly tone
- Structure documents with clear headings and bullet points
- Include actionable items with concrete timelines
- Reference company policies when context is provided
- Never use generic placeholder text like [Company Name] — use the details provided
- Format output in clean Markdown"""


# ─────────────────────────────────────────────────────────────
# Step 1: Parse Data — validation summary
# ─────────────────────────────────────────────────────────────

PARSE_DATA_PROMPT = """Analyze and validate the following new hire data. Summarize the employee profile and flag any missing or potentially incorrect information.

**Employee Details:**
- Name: {name}
- Email: {email}
- Role: {role}
- Department: {department}
- Start Date: {start_date}
- Manager Email: {manager_email}
- Buddy Email: {buddy_email}

Provide a brief validation summary including:
1. Data completeness check
2. Any fields that need attention (e.g., missing manager or buddy)
3. A one-line readiness assessment"""


# ─────────────────────────────────────────────────────────────
# Step 2: Welcome Email
# ─────────────────────────────────────────────────────────────

WELCOME_EMAIL_PROMPT = """Generate a warm, professional welcome email for a new employee joining the team.

**New Hire Details:**
- Name: {name}
- Role: {role}
- Department: {department}
- Start Date: {start_date}
- Manager: {manager_email}
- Onboarding Buddy: {buddy_email}

The email should:
1. Welcome them enthusiastically to the team
2. Confirm their start date and first-day schedule
3. Introduce their manager and buddy by name
4. List what to expect during their first week:
   - Day 1: Orientation, IT setup, team introductions
   - Day 2: Manager 1:1, tool walkthroughs
   - Day 3: Buddy meetup, department deep-dive
5. Provide practical tips (dress code, parking, what to bring)
6. Include contact information for questions
7. End with an encouraging closing

Format as a complete email with Subject line, greeting, body, and sign-off."""


# ─────────────────────────────────────────────────────────────
# Step 3: Offer Letter
# ─────────────────────────────────────────────────────────────

OFFER_LETTER_PROMPT = """Generate a formal offer letter / employment confirmation for:

**Employee Details:**
- Name: {name}
- Role: {role}
- Department: {department}
- Start Date: {start_date}
- Reporting To: {manager_email}

The offer letter should include:
1. A formal header with company details
2. Position title and department confirmation
3. Start date and reporting structure
4. A section for compensation details (use placeholder amounts)
5. Benefits overview (health insurance, PTO, retirement plan)
6. Employment terms (at-will employment, probationary period)
7. Confidentiality and IP agreement reference
8. Acceptance instructions and signature block
9. A warm closing expressing excitement about them joining

Use a formal but welcoming tone. Format as a professional business letter."""


# ─────────────────────────────────────────────────────────────
# Step 4: 30-60-90 Day Plan
# ─────────────────────────────────────────────────────────────

PLAN_30_60_90_PROMPT = """Create a comprehensive 30-60-90 day onboarding plan tailored to this role:

**Employee Details:**
- Name: {name}
- Role: {role}
- Department: {department}
- Start Date: {start_date}
- Manager: {manager_email}

Structure the plan as follows:

**First 30 Days — Learn & Orient**
- Specific learning objectives for the {role} role in {department}
- Key people to meet and relationships to build
- Training modules and documentation to review
- Tools and systems to master
- Weekly check-in milestones

**Days 31-60 — Contribute & Collaborate**
- Initial project assignments appropriate for the role
- Cross-functional collaboration opportunities
- Skill development goals
- Feedback checkpoints with manager

**Days 61-90 — Own & Deliver**
- Independent project ownership
- Performance metrics and success criteria
- Team presentation or knowledge sharing
- Goal setting for the next quarter
- 90-day review preparation

Make each phase specific to the {role} role in the {department} department.
Include 4-6 concrete action items per phase."""


# ─────────────────────────────────────────────────────────────
# Step 5: Schedule Events — handled by calendar service, no LLM needed
# ─────────────────────────────────────────────────────────────

# (No prompt template needed — this step uses the calendar service directly)


# ─────────────────────────────────────────────────────────────
# Step 6: Equipment Request
# ─────────────────────────────────────────────────────────────

EQUIPMENT_REQUEST_PROMPT = """Generate an IT equipment and software provisioning request for:

**Employee Details:**
- Name: {name}
- Role: {role}
- Department: {department}
- Start Date: {start_date}

Create a detailed provisioning checklist including:

**Hardware:**
- Primary workstation (recommend laptop vs desktop based on the role)
- Monitors and peripherals
- Mobile device if applicable
- Any role-specific hardware (e.g., drawing tablet for designers)

**Software & Licenses:**
- Standard suite (email, calendar, chat, video conferencing)
- Department-specific tools for the {department} team
- Development tools if applicable for {role}
- Security software (VPN, MFA setup)

**Access & Accounts:**
- Email and directory setup
- Internal systems and dashboards
- Code repositories or document management (role-dependent)
- Physical access (badge, office keys)

**Timeline:**
- What must be ready before Day 1
- What can be set up during the first week
- Estimated total provisioning time

Format as a structured IT request form with clear categories and checkboxes."""
