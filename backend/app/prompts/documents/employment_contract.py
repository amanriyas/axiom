# app/prompts/documents/employment_contract.py
"""Prompt template for generating jurisdiction-aware employment contracts."""

EMPLOYMENT_CONTRACT_PROMPT = """Generate a formal, legally compliant employment contract for the following employee.

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
4. Maintain formal legal language appropriate for the jurisdiction
5. Include all standard employment clauses (duties, compensation, benefits, termination, etc.)
6. Add proper headers, section numbering, and signature blocks
7. If no jurisdiction template is available, create a comprehensive contract following best practices for the specified jurisdiction
8. Do NOT use generic placeholders — fill in all known details

Format the output as a complete, ready-to-sign employment contract in Markdown."""
