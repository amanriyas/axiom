# app/prompts/documents/equity_agreement.py
"""Prompt template for generating equity/stock option agreements."""

EQUITY_AGREEMENT_PROMPT = """Generate a formal equity/stock option agreement for the following employee.

**Employee Details:**
- Name: {name}
- Role: {role}
- Department: {department}
- Start Date: {start_date}
- Jurisdiction: {jurisdiction}

**Instructions:**
1. Create a comprehensive equity incentive agreement appropriate for {jurisdiction}
2. Include standard vesting schedule (4-year vesting with 1-year cliff)
3. Cover the following sections:
   - Grant details (placeholder for number of shares/options)
   - Vesting schedule and cliff period
   - Exercise price and exercise window
   - Change of control / acceleration provisions
   - Termination scenarios (voluntary, involuntary, for cause)
   - Tax implications notice for {jurisdiction}
   - Transfer restrictions
   - Company repurchase rights
4. Use language appropriate for the {role} level in {department}
5. Include proper definitions section
6. Add signature blocks for both parties
7. Reference applicable securities laws for {jurisdiction}

Note: Use placeholder values for specific share counts and exercise prices (e.g., "[X,XXX shares]", "[$X.XX per share]").

Format the output as a complete equity agreement in Markdown."""
