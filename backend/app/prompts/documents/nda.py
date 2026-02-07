# app/prompts/documents/nda.py
"""Prompt template for generating jurisdiction-aware NDAs."""

NDA_PROMPT = """Generate a formal Non-Disclosure Agreement (NDA) for the following employee.

**Employee Details:**
- Name: {name}
- Role: {role}
- Department: {department}
- Start Date: {start_date}
- Jurisdiction: {jurisdiction}

**Jurisdiction Template (use as the base structure):**
{jurisdiction_template}

**Legal Requirements for this jurisdiction:**
{legal_requirements}

**Instructions:**
1. Use the jurisdiction template as the structural foundation
2. Personalize all placeholders with the employee's actual details
3. Ensure ALL legal requirements listed above are addressed
4. Define "Confidential Information" broadly but precisely
5. Include clear obligations, exceptions, duration, and remedies
6. Add role-specific confidentiality considerations for {role} in {department}
7. Include proper signature blocks
8. Maintain legal language appropriate for {jurisdiction}

Format the output as a complete, ready-to-sign NDA in Markdown."""
