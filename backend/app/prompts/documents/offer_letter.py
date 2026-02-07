# app/prompts/documents/offer_letter.py
"""Prompt template for generating jurisdiction-aware offer letters as formal documents."""

OFFER_LETTER_DOCUMENT_PROMPT = """Generate a formal offer letter for the following employee, compliant with {jurisdiction} employment law.

**Employee Details:**
- Name: {name}
- Role: {role}
- Department: {department}
- Start Date: {start_date}
- Reporting To: {manager_email}
- Jurisdiction: {jurisdiction}

**Jurisdiction Template (use as the base structure):**
{jurisdiction_template}

**Legal Requirements for this jurisdiction:**
{legal_requirements}

**Instructions:**
1. Use the jurisdiction template as the structural foundation
2. Personalize all placeholders with the employee's actual details
3. Ensure ALL legal requirements listed above are addressed
4. Include:
   - Position and department confirmation
   - Start date and reporting structure
   - Compensation details (use placeholder amounts)
   - Benefits overview appropriate for {jurisdiction}
   - Employment terms specific to {jurisdiction}
   - Any required legal disclaimers for the jurisdiction
   - Acceptance instructions and deadline
   - Signature block
5. Maintain a professional but welcoming tone
6. Reference jurisdiction-specific benefits and regulations

Format the output as a complete, ready-to-sign offer letter in Markdown."""
